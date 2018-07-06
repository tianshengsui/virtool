import os
import shutil

import virtool.db.files
import virtool.jobs.job
import virtool.samples
import virtool.utils


def force_makedirs(path):
    try:
        os.makedirs(os.path.join(path, "analysis"))
    except OSError:
        # If the path already exists, remove it and try again.
        shutil.rmtree(path)
        os.makedirs(os.path.join(path, "analysis"))


def move_trimming_results(path, paired):
    if paired:
        shutil.move(
            os.path.join(path, "reads-trimmed-pair1.fastq"),
            os.path.join(path, "reads_1.fastq")
        )

        shutil.move(
            os.path.join(path, "reads-trimmed-pair2.fastq"),
            os.path.join(path, "reads_2.fastq")
        )

    else:
        shutil.move(
            os.path.join(path, "reads-trimmed.fastq"),
            os.path.join(path, "reads_1.fastq")
        )

    shutil.move(
        os.path.join(path, "reads-trimmed.log"),
        os.path.join(path, "trim.log")
    )


class CreateSample(virtool.jobs.job.Job):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #: The id assigned to the new sample.
        self.sample_id = self.task_args["sample_id"]

        #: The path where the files for this sample are stored.
        self.sample_path = os.path.join(self.settings.get("data_path"), "samples", str(self.sample_id))

        #: The path where FASTQC results will be written.
        self.fastqc_path = os.path.join(self.sample_path, "fastqc")

        #: The names of the reads files in the files path used to create the sample.
        self.files = self.task_args["files"]

        #: Is the sample library paired or not.
        self.paired = len(self.files) == 2

        #: The ordered list of :ref:`stage methods <stage-methods>` that are called by the job.
        self._stage_list = [
            self.make_sample_dir,
            self.trim_reads,
            self.save_trimmed,
            self.fastqc,
            self.parse_fastqc,
            self.clean_watch
        ]

    @virtool.jobs.job.stage_method
    async def make_sample_dir(self):
        """
        Make a data directory for the sample and a subdirectory for analyses. Read files, quality data from FastQC, and
        analysis data will be stored here.

        """
        await self.run_in_executor(force_makedirs, self.sample_path)

    @virtool.jobs.job.stage_method
    async def trim_reads(self):
        """
        Trim the reads by calling Skewer.

        """
        input_paths = [os.path.join(self.settings.get("data_path"), "files", file_id) for file_id in self.files]

        command = [
            "skewer",
            "-m", "pe" if self.paired else "any",
            "-l", "20" if self.task_args["srna"] else "50",
            "-q", "20",
            "-Q", "25",
            "-t", str(self.settings.get("create_sample_proc")),
            "-o", os.path.join(self.sample_path, "reads"),
            "--quiet"
        ]

        # Trim reads to max length of 23 if the sample is sRNA.
        if self.task_args["srna"]:
            command += [
                "-L", "23",
                "-e"
            ]

        command += input_paths

        # Prevents an error from skewer when called inside a subprocess.
        env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

        await self.run_subprocess(command, env=env)

    @virtool.jobs.job.stage_method
    async def save_trimmed(self):
        """
        Give the trimmed FASTQ and log files generated by skewer more readable names.

        """
        await self.run_in_executor(move_trimming_results, self.sample_path, self.paired)

    @virtool.jobs.job.stage_method
    async def fastqc(self):
        """
        Runs FastQC on the renamed, trimmed read files.

        """
        self.loop.run_in_executor(None, os.mkdir, os.path.join(self.sample_path, "fastqc"))

        command = [
            "fastqc",
            "-f", "fastq",
            "-o", self.fastqc_path,
            "-t", "2",
            "--extract",
            self.sample_path + "/reads_1.fastq"
        ]

        if self.paired:
            command.append(os.path.join(self.sample_path, "reads_2.fastq"))

        await self.run_subprocess(command)

    @virtool.jobs.job.stage_method
    async def parse_fastqc(self):
        """
        Capture the desired data from the FastQC output. The data is added to the samples database
        in the main run() method

        """
        # Get the text data files from the FastQC output
        for name in os.listdir(self.fastqc_path):
            if "reads" in name and "." not in name:
                suffix = name.split("_")[1]
                shutil.move(
                    os.path.join(self.fastqc_path, name, "fastqc_data.txt"),
                    os.path.join(self.sample_path, "fastqc_{}.txt".format(suffix))
                )

        # Dispose of the rest of the data files.
        shutil.rmtree(self.sample_path + "/fastqc")

        fastqc = {
            "count": 0
        }

        # Parse data file(s)
        for suffix in [1, 2]:
            path = os.path.join(self.sample_path, "fastqc_{}.txt".format(suffix))

            try:
                handle = open(path, "r")
            except IOError:
                if suffix == 2:
                    continue
                else:
                    raise

            flag = None

            for line in handle:
                # Turn off flag if the end of a module is encountered
                if flag is not None and "END_MODULE" in line:
                    flag = None

                # Total sequences
                elif "Total Sequences" in line:
                    fastqc["count"] += int(line.split("\t")[1])

                # Read encoding (eg. Illumina 1.9)
                elif "encoding" not in fastqc and "Encoding" in line:
                    fastqc["encoding"] = line.split("\t")[1]

                # Length
                elif "Sequence length" in line:
                    min_length, max_length = [int(s) for s in line.split("\t")[1].split('-')]

                    if suffix == 1:
                        fastqc["length"] = [min_length, max_length]
                    else:
                        fastqc_min_length, fastqc_max_length = fastqc["length"]

                        fastqc["length"] = [
                            min(fastqc_min_length, min_length),
                            max(fastqc_max_length, max_length)
                        ]

                # GC-content
                elif "%GC" in line and "#" not in line:
                    gc = float(line.split("\t")[1])

                    if suffix == 1:
                        fastqc["gc"] = gc
                    else:
                        fastqc["gc"] = (fastqc["gc"] + gc) / 2

                # The statements below handle the beginning of multi-line FastQC sections. They set the flag
                # value to the found section and allow it to be further parsed.
                elif "Per base sequence quality" in line:
                    flag = "bases"
                    if suffix == 1:
                        fastqc[flag] = [None] * fastqc["length"][1]

                elif "Per sequence quality scores" in line:
                    flag = "sequences"
                    if suffix == 1:
                        fastqc[flag] = [0] * 50

                elif "Per base sequence content" in line:
                    flag = "composition"
                    if suffix == 1:
                        fastqc[flag] = [None] * fastqc["length"][1]

                # The statements below handle the parsing of lines when the flag has been set for a multi-line
                # section. This ends when the 'END_MODULE' line is encountered and the flag is reset to none
                elif flag in ["composition", "bases"] and "#" not in line:
                    # Split line around whitespace.
                    split = line.rstrip().split()

                    # Convert all fields except first to 2-decimal floats.
                    values = [round(int(value.split(".")[0]), 1) for value in split[1:]]

                    # Convert to position field to a one- or two-member tuple.
                    pos = [int(x) for x in split[0].split('-')]

                    if len(pos) > 1:
                        pos = range(pos[0], pos[1] + 1)
                    else:
                        pos = [pos[0]]

                    if suffix == 1:
                        for i in pos:
                            fastqc[flag][i - 1] = values
                    else:
                        for i in pos:
                            fastqc[flag][i - 1] = virtool.utils.average_list(fastqc[flag][i - 1], values)

                elif flag == "sequences" and "#" not in line:
                    line = line.rstrip().split()

                    quality = int(line[0])

                    fastqc["sequences"][quality] += int(line[1].split(".")[0])

        await self.db.samples.update_one({"_id": self.sample_id}, {
            "$set": {
                "quality": fastqc,
                "imported": False
            }
        })

    @virtool.jobs.job.stage_method
    async def clean_watch(self):
        """ Remove the original read files from the files directory """
        for file_id in self.files:
            await virtool.db.files.remove(self.loop, self.db, self.settings, file_id)

    async def cleanup(self):
        await virtool.db.files.release_reservations(self.db, self.task_args["files"])

        try:
            await self.loop.run_in_executor(None, shutil.rmtree, self.sample_path)
        except FileNotFoundError:
            pass

        await self.db.samples.delete_one({"_id": self.sample_id})

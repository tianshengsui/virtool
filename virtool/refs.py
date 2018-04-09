import gzip
import json

import virtool.kinds


async def get_owner_user(user_id):
    return {
        "id": user_id,
        "modify": True,
        "modify_kind": True,
        "remove": True
    }


def validate_kinds(kinds):
    fields = ["_id", "name", "abbreviation"]

    seen = {field: set() for field in fields + ["isolate_id", "sequence_id"]}
    duplicates = {field: set() for field in fields + ["isolate_id", "sequence_id"]}

    errors = dict()

    for joined in kinds:
        # Check for problems local to the kind document.
        errors[joined["name"].lower()] = virtool.kinds.validate_kind(joined)

        # Check for problems in the list as a whole.
        for field in fields:
            value = joined[field]

            if field == "abbreviation" and value == "":
                continue

            if field == "name":
                value = value.lower()

            if value in seen[field]:
                duplicates[field].add(value)
            else:
                seen[field].add(value)

        for isolate in joined["isolates"]:
            if "isolate_id" in isolate:
                isolate["id"] = isolate.pop("isolate_id")

            isolate_id = isolate["id"]

            if isolate_id in seen:
                duplicates["isolate_id"].add(isolate_id)
            else:
                seen["isolate_id"].add(isolate_id)

            for sequence in isolate["sequences"]:
                sequence_id = sequence.get("id", sequence["_id"])

                if sequence_id in seen["sequence_id"]:
                    duplicates["sequence_id"].add(sequence_id)
                else:
                    seen["sequence_id"].add(sequence_id)

    if not any(duplicates.values()):
        duplicates = None
    else:
        duplicates = {key: list(duplicates[key]) for key in duplicates}

    if any(errors.values()):
        errors = {key: errors[key] for key in errors if errors[key]}
    else:
        errors = None

    return duplicates, errors


def load_import_file(path):
    """
    Load a list of merged kinds documents from a file handle associated with a Virtool ``kinds.json.gz`` file.

    :param path: the path to the kinds.json.gz file
    :type path: str

    :return: the kinds data to import
    :rtype: dict

    """
    with open(path, "rb") as handle:
        with gzip.open(handle, "rt") as gzip_file:
            return json.load(gzip_file)


async def send_import_dispatches(dispatch, insertions, replacements, flush=False):
    """
    Dispatch all possible insertion and replacement messages for a running kinds reference import. Called many times
    during an import process.

    :param dispatch: the dispatch function
    :type dispatch: func

    :param insertions: a list of tuples describing insertions
    :type insertions: list

    :param replacements: a list of tuples describing replacements and their component removals and an insertions
    :type replacements: list

    :param flush: override the length check and flush all data to the dispatcher
    :type flush: bool

    """

    if len(insertions) == 30 or (flush and insertions):
        kind_updates, history_updates = zip(*insertions)

        await dispatch("kinds", "update", kinds_updates)
        await dispatch("history", "update", history_updates)

        del insertions[:]

    if len(replacements) == 30 or (flush and replacements):
        await dispatch("kinds", "remove", [replace[0][0] for replace in replacements])
        await dispatch("history", "update", [replace[0][1] for replace in replacements])

        await dispatch("kinds", "update", [replace[1][0] for replace in replacements])
        await dispatch("history", "update", [replace[1][1] for replace in replacements])

        del replacements[:]

import {
    getSoftwareUpdates,
    installSoftwareUpdates
} from "./actions";

describe("Updates Action Creators:", () => {

    it("getSoftwareUpdates: returns simple action", () => {
        const result = getSoftwareUpdates();
        const expected = {
            type: "GET_SOFTWARE_UPDATES_REQUESTED"
        };

        expect(result).toEqual(expected);
    });

    it("install: returns simple action", () => {
        const result = installSoftwareUpdates();
        const expected = {
            type: "INSTALL_SOFTWARE_UPDATES_REQUESTED"
        };

        expect(result).toEqual(expected);
    });
});

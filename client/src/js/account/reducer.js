/**
 * Exports a reducer for dealing with the account of the session user.
 *
 * @module account/reducer
 */
import {
    GET_ACCOUNT,
    UPDATE_ACCOUNT,
    UPDATE_ACCOUNT_SETTINGS,
    CHANGE_ACCOUNT_PASSWORD,
    GET_API_KEYS,
    CREATE_API_KEY,
    CLEAR_API_KEY,
    LOGOUT
} from "../app/actionTypes";

/**
 * The state that should initially be stored.
 *
 * @const
 * @type {object}
 */
export const initialState = {
    ready: false,
    oldPasswordError: false,
    apiKeys: null,
    newKey: null
};

/**
 * A reducer for dealing with the account of the session user.
 *
 * @param state {object}
 * @param action {object}
 * @returns {object}
 */
export default function accountReducer(state = initialState, action) {
    switch (action.type) {
        case GET_ACCOUNT.SUCCEEDED:
            return { ...state, ...action.data, ready: true };

        case UPDATE_ACCOUNT.SUCCEEDED:
            return { ...state, ...action.data };

        case GET_API_KEYS.SUCCEEDED:
            return { ...state, apiKeys: action.data };

        case CHANGE_ACCOUNT_PASSWORD.SUCCEEDED:
            return { ...state, oldPasswordError: false };

        case CREATE_API_KEY.REQUESTED:
            return { ...state, key: null };

        case CREATE_API_KEY.SUCCEEDED:
            return { ...state, newKey: action.data.key };

        case CLEAR_API_KEY:
            return { ...state, newKey: null };

        case UPDATE_ACCOUNT_SETTINGS.SUCCEEDED:
            return { ...state, settings: action.data };

        case LOGOUT.SUCCEEDED:
            return { ...initialState };

        default:
            return state;
    }
}

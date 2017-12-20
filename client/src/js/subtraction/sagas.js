import { push } from "react-router-redux";
import { put, takeLatest, throttle } from "redux-saga/effects";

import subtractionAPI from "./api";
import { apiCall, pushHistoryState, putGenericError, setPending } from "../sagaUtils";
import {
    FIND_SUBTRACTIONS,
    LIST_SUBTRACTION_IDS,
    GET_SUBTRACTION,
    CREATE_SUBTRACTION,
    REMOVE_SUBTRACTION
} from "../actionTypes";

export function* findSubtractions (action) {
    yield setPending(apiCall(subtractionAPI.find, action, FIND_SUBTRACTIONS));
}

export function* listSubtractionIds (action) {
    yield setPending(apiCall(subtractionAPI.listIds, action, LIST_SUBTRACTION_IDS));
}

export function* getSubtraction (action) {
    yield setPending(apiCall(subtractionAPI.get, action, GET_SUBTRACTION));
}

export function* createSubtraction (action) {
    yield setPending(function* (action) {
        try {
            yield subtractionAPI.create(action.subtractionId, action.fileId);
            yield put({type: FIND_SUBTRACTIONS.REQUESTED});
            yield pushHistoryState({createSubtraction: false});
        } catch (error) {
            yield putGenericError(CREATE_SUBTRACTION, error);
        }
    }, action);
}

export function* removeSubtraction (action) {
    yield setPending(function* () {
        yield apiCall(subtractionAPI.remove, action, REMOVE_SUBTRACTION);
        yield put(push("/subtraction"));
    });
}

export function* watchSubtraction () {
    yield throttle(500, FIND_SUBTRACTIONS.REQUESTED, findSubtractions);
    yield takeLatest(LIST_SUBTRACTION_IDS.REQUESTED, listSubtractionIds);
    yield takeLatest(GET_SUBTRACTION.REQUESTED, getSubtraction);
    yield throttle(500, CREATE_SUBTRACTION.REQUESTED, createSubtraction);
    yield throttle(300, REMOVE_SUBTRACTION.REQUESTED, removeSubtraction);
}

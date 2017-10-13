/**
 * @license
 * The MIT License (MIT)
 * Copyright 2015 Government of Canada
 *
 * @author
 * Ian Boyes
 *
 * @exports Help
 */

import React from "react";
import PropTypes from "prop-types";
import CX from "classnames";
import { Popover, OverlayTrigger } from "react-bootstrap";
import { Icon } from "./Icon";

export const Help = (props) => {

    const popover = (
        <Popover title={props.title} id="help-popover">
            {props.children}
        </Popover>
    );

    const classes = CX("pointer", {
        "pull-right": props.pullRight
    });

    return (
        <OverlayTrigger trigger="click" placement="top" overlay={popover} rootClose>
            <span className={classes}>
                <Icon name="question" />
            </span>
        </OverlayTrigger>
    );
};

Help.propTypes = {
    title: PropTypes.string,
    pullRight: PropTypes.bool,
    children: PropTypes.node.isRequired
};
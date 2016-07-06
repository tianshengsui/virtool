/**
 * @license
 * The MIT License (MIT)
 * Copyright 2015 Government of Canada
 *
 * @author
 * Ian Boyes
 *
 * @exports JobError
 */

'use strict';

var _ = require('lodash');
var React = require('react');
var Panel = require('react-bootstrap/lib/Panel');
var Alert = require('react-bootstrap/lib/Alert');

/**
 * A render-only panel that displays the error information for a failed job.
 */
var JobError = React.createClass({

    propTypes: {
        error: React.PropTypes.object.isRequired
    },

    shouldComponentUpdate: function () {
        return false;
    },

    render: function () {
        console.log(this.props);

        // The content to place inside the error panel.
        var content;

        if (this.props.error.context.indexOf('External') === -1) {
            // Traceback from a Python exception.
            var tracebackLines = this.props.error.message.traceback.map(function (line) {
                return <span className='block-display traceback-line'>{line}</span>;
            });

            // Only show a colon and exception detail after the exception name if there is detail present.
            var details;

            if (this.props.error.message.details.length > 0) {
                details = <span>: {this.props.error.message.details}</span>
            }

            // Content replicates format of Python exceptions shown in Python console.
            content = (
                <div>
                    <span className='block-display'>Traceback (most recent call last):</span>
                    {tracebackLines}
                    <p className='block-display'>{this.props.error.message.type}{details}</p>
                </div>
            );
        } else {
            // An error in an external application.
            content = this.props.error.message.map(function (line) {
                return <p>{line}</p>
            });
        }

        return (
            <Alert bsStyle='danger'>
                <h5><strong>{this.props.error.context}</strong></h5>
                {content}
            </Alert>
        );
    }
});

module.exports = JobError;
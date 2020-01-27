import { get } from "lodash-es";
import React from "react";
import { connect } from "react-redux";
import styled from "styled-components";
import { BoxGroup, BoxGroupHeader, BoxGroupSection, InputError, SaveButton } from "../../base";
import { clearError } from "../../errors/actions";
import { updateAccount } from "../actions";

const FormButton = styled(BoxGroupSection)`
    height: 154px;
`;

const getInitialState = email => ({
    email: email || "",
    error: ""
});

const re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

export class Email extends React.Component {
    constructor(props) {
        super(props);
        this.state = getInitialState(this.props.email);
    }

    static getDerivedStateFromProps(nextProps, prevState) {
        if (nextProps.error === "Invalid input" && !prevState.error.length) {
            return { error: "Please provide a valid email address" };
        }
        return null;
    }

    handleChange = e => {
        this.setState({
            email: e.target.value,
            error: ""
        });

        if (this.props.error) {
            this.props.onClearError("UPDATE_ACCOUNT_ERROR");
        }
    };

    handleBlur = e => {
        if (!e.relatedTarget) {
            this.setState({
                email: this.props.email,
                error: ""
            });
        }
    };

    handleSubmit = e => {
        e.preventDefault();

        if (!re.test(this.state.email)) {
            this.setState({ error: "Please provide a valid email address" });
            return;
        }

        this.props.onUpdateEmail(this.state.email);
    };

    render() {
        return (
            <BoxGroup>
                <BoxGroupHeader>
                    <h2>Email</h2>
                </BoxGroupHeader>
                <FormButton>
                    <form onSubmit={this.handleSubmit}>
                        <InputError
                            label="Email address"
                            value={this.state.email}
                            onChange={this.handleChange}
                            onBlur={this.handleBlur}
                            error={this.state.error}
                        />
                        <SaveButton pullRight />
                    </form>
                </FormButton>
            </BoxGroup>
        );
    }
}

const mapStateToProps = state => ({
    email: state.account.email,
    error: get(state, "errors.UPDATE_ACCOUNT_ERROR.message", "")
});

const mapDispatchToProps = dispatch => ({
    onUpdateEmail: email => {
        dispatch(updateAccount(email));
    },

    onClearError: error => {
        dispatch(clearError(error));
    }
});

export default connect(mapStateToProps, mapDispatchToProps)(Email);

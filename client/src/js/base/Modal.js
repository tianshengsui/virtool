import React from "react";
import { Modal as BsModal } from "react-bootstrap";

import { DialogOverlay, DialogContent } from "@reach/dialog";

import styled, { keyframes } from "styled-components";
import { BoxGroupSection, Box } from "./Box";
import { Alert } from "./Alert";

export const Modal = styled(BsModal)`
    ${Alert} {
        border-left: none;
        border-radius: 0;
        border-right: none;
        margin: -1px 0 0;
    }
`;

const modalOverlayOpen = keyframes`
    0% {
        opacity: 0;
    }
`;

const modalOverlayClose = keyframes`
    100% {
      opacity: 0;
    }
`;

const modalContentOpen = keyframes`
    100% {
        transform: translate(0,100px);
    }
`;

const modalContentClose = keyframes`
    0% {
        transform: translate(0,100px);
    }
    100% {
        opacity: 0;
    }
`;
export const ModalDialogOverlay = styled(({ close, ...rest }) => <DialogOverlay {...rest} />)`
    animation: ${props => (props.close ? modalOverlayClose : modalOverlayOpen)} 0.3s;
    animation-fill-mode: forwards;
    background: hsla(0, 0%, 0%, 0.33);
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    overflow: auto;
    position: fixed;
    z-index: 9999;
`;

export const ModalDialogContent = styled(({ close, size, ...rest }) => <DialogContent {...rest} />)`
    animation: ${props => (props.close ? modalContentClose : modalContentOpen)} 0.3s;
    animation-fill-mode: forwards;
    background: white;
    box-shadow: rgba(0, 0, 0, 0.5) 0 5px 15px;
    margin: -70px auto;
    padding: 0;
    position: relative;
    width: ${props => (props.size === "lg" ? "900px" : "600px")};

    @media (max-width: 991px) {
        width: 600px;
    }
`;

export const DialogHeader = styled(({ modalStyle, headerBorderBottom, capitalize, ...rest }) => (
    <BoxGroupSection {...rest} />
))`
    background-color: ${props => (props.modalStyle === "danger" ? "#d44b40" : "")};
    color: ${props => (props.modalStyle === "danger" ? "white" : "")};
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: ${props => props.headerBorderBottom} !important;
    text-transform: ${props => props.capitalize};
`;

export const DialogBody = styled.div`
    padding: 15px;
`;

<<<<<<< 7f895b5b7da896b0162356599074b00ef990069b
export const DialogFooter = styled(Box)`
    display: flex;
    justify-content: end;
=======
export const DialogFooter = styled(({ modalStyle, ...rest }) => <Box {...rest} />)`
    border-top: ${props => (props.modalStyle === "danger" ? "none" : "")}
>>>>>>> Replace bootstrap modal in base RemoveModal Component
    border-bottom: none;
`;

export class ModalDialog extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            open: false,
            close: false
        };
    }

    static getDerivedStateFromProps(props) {
        if (props.show === true) {
            return {
                open: true
            };
        }
        return null;
    }

    onClose = () => {
        this.setState({ close: true });
    };

    onClosed = () => {
        if (this.state.close === true) {
            this.setState({ open: false, close: false });

            if (this.props.onExited) {
                this.props.onExited();
            }
        }
    };

    onOpen = () => {
        if (this.state.open === true && this.state.close === false && this.props.onEnter) {
            this.props.onEnter();
        }
    };

    render() {
        return (
            <div>
                <ModalDialogOverlay
                    isOpen={this.state.open}
                    close={this.state.close}
                    onAnimationEnd={this.onClosed}
                    onDismiss={() => {
                        this.props.onHide();
                        this.onClose();
                    }}
                >
                    <ModalDialogContent
                        size={this.props.size}
                        aria-labelledby={this.props.label}
                        close={this.state.close}
                        onAnimationEnd={this.onClosed}
                        onAnimationStart={this.onOpen}
                    >
                        <DialogHeader
                            modalStyle={this.props.modalStyle}
                            headerBorderBottom={this.props.headerBorderBottom}
                            capitalize={this.props.capitalize}
                        >
                            {this.props.headerText}
                            {CloseButton}
                        </DialogHeader>
>>>>>>> Replace bootstrap modal in base RemoveModal Component
                        {this.props.children}
                    </ModalDialogContent>
                </ModalDialogOverlay>
            </div>
        );
    }
}

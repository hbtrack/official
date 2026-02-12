# AI Workflow Documentation

## 1. Introduction
This document outlines the comprehensive AI agent workflow for the project, aimed at providing clarity for developers and users. It details the handshake requirements to establish communication with the AI agent.

## 2. Handshake Protocol
The handshake protocol is mandatory for establishing a secure communication channel with the AI agent. The protocol includes three stages:
- **ACK**: Acknowledge receipt.
- **ASK**: Request for action.
- **EXECUTE**: Execute the command sent by the agent.

Refer to the exact format from [.github/copilot-handshake.md](https://github.com/Davisermenho/Hb_Track/blob/main/.github/copilot-handshake.md).

## 3. Agent Workflow
The agent follows a 5-step process outlined in the quick start routing:
- **Step 1**: Initialize the session.
- **Step 2**: Validate input data.
- **Step 3**: Execute the command.
- **Step 4**: Handle results and errors.
- **Step 5**: Complete the transaction.

For more details, see [docs/_ai/_INDEX.md](https://github.com/Davisermenho/Hb_Track/blob/main/docs/_ai/_INDEX.md).

## 4. Approved Commands
### PowerShell Commands
- **Category 1**: Commands related to environment set-up.
- **Category 2**: Commands for data processing.

See the full list in [docs/_ai/_context/approved-commands.yml](https://github.com/Davisermenho/Hb_Track/blob/main/docs/_ai/_context/approved-commands.yml).

## 5. Exit Code Contract
Exit codes are categorized as follows:
- **0**: Successful execution.
- **1**: Minor issue (retrievable).
- **2**: Encountered an error but continues.
- **3**: Fatal error.
- **4**: PENDENTE (to be defined).
Refer to [docs/_ai/_maps/troubleshooting-map.json](https://github.com/Davisermenho/Hb_Track/blob/main/docs/_ai/_maps/troubleshooting-map.json) for references on troubleshooting based on exit codes.

## 6. Artifact Consumption
This section explains how to utilize generated YAML and JSON files for further processing and command execution.

## 7. Guardrails
Policies must align with the following:
- **GUARDRAIL_POLICY_PARITY.md**
- **GUARDRAIL_POLICY_BASELINE.md**
- **GUARDRAIL_POLICY_REQUIREMENTS.md**

Refer to the guardrails documentation for details situated in [docs/_ai/_guardrails/](https://github.com/Davisermenho/Hb_Track/blob/main/docs/_ai/_guardrails/).

## 8. Validation Workflow
This section describes the sequence of gates that need to be crossed before executing commands:
- Validation steps outline essential checks before proceeding to execution.

## 9. Recovery Paths
Possible troubleshooting steps based on exit codes are outlined in the troubleshooting map.

## 10. Quality Gates
The quality gates consist of pre-defined scripts that require evidence of validation before executing commands. Missing validation commands are marked as **PENDENTE**.

---

This document is designed to provide a structured approach to the AI agent workflow, ensuring clarity, consistency, and efficiency in execution processes.
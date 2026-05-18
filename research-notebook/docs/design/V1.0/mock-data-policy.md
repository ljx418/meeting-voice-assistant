# ResearchNotebook V1.0 Mock Data Policy

文档状态：P1 implementation policy。
适用阶段：M0-M1 and future shell work。

## 1. Purpose

M0 may use static or mocked data to build visual shells. Mock data must never be confused with production capability.

## 2. Allowed Mock Use

Allowed:

- AppShell visual states;
- Home empty/loading examples;
- Workbench layout examples;
- disabled future shell screens;
- component state fixtures for loading/error/empty states.

## 3. Forbidden Mock Use

Forbidden as product capability:

- mock question generation;
- mock attempt scoring;
- mock mastery profile;
- fake JSON/PPT/video/audio parser readiness;
- fake precise citation locators;
- fake correction apply.

## 4. Labeling Rules

Mock-only or future-shell UI must be:

- disabled;
- visibly marked as unavailable/dev-only where user-facing;
- excluded from release acceptance;
- backed by route matrix status `future backend phase` or `unsupported in V1.0`.

## 5. Acceptance

No V1.0 demo or release note may present mock future-shell behavior as working product capability.

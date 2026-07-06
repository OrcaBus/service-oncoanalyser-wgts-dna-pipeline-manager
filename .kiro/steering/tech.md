# Tech Stack

## Languages

- **TypeScript** — CDK infrastructure code (ES2020, strict mode, `commonjs` modules)
- **Python** — Lambda business logic (Python 3.14, ARM64)

## Infrastructure

- **AWS CDK v2** (`aws-cdk-lib ^2.259.0`) with TypeScript
- **`@orcabus/platform-cdk-constructs`** — internal shared constructs library (pinned to `1.7.1`)
- **`@aws-cdk/aws-lambda-python-alpha`** — Python Lambda bundling via `PythonUvFunction` (uses `uv`)
- **cdk-nag** (`^2.38.2`) — CDK security/compliance rule checks in tests

## Key AWS Services Used

- **AWS Lambda** (Python, ARM64, 512 MB default / 1024 MB with ICAv2 layer or pandas, 60s timeout)
- **AWS Step Functions** (ASL JSON templates in `app/step-functions-templates/`)
- **Amazon EventBridge** — event bus `OrcaBusMain`, source `orcabus.oncoanalyserwgtsdna`
- **AWS SSM Parameter Store** — configuration under `/orcabus/workflows/oncoanalyser-wgts-dna/`
- **AWS Schemas Registry** — JSON schema validation for draft events

## Package Manager

**pnpm** (v11.7.0). Always use `pnpm`, never `npm` or `yarn`.

```sh
corepack enable pnpm
```

## Node Version

Node 22.9.0

## Build / Test / Lint Commands

```sh
# Install dependencies
make install          # runs: pnpm install --frozen-lockfile

# Run all checks (audit, prettier, eslint, pre-commit)
make check

# Auto-fix lint and formatting issues
make fix

# Run TypeScript compile + Jest tests
make test             # runs: pnpm test (tsc && jest)

# CDK commands
pnpm cdk-stateless <cmd>   # stateless stack (Lambdas, Step Functions, event rules)
pnpm cdk-stateful <cmd>    # stateful stack (SSM params, Schemas registry)

# List stacks
pnpm cdk-stateless ls
pnpm cdk-stateful ls
```

## Linting & Formatting

- **ESLint** (`eslint.config.mjs`) with `typescript-eslint`
- **Prettier** (`.prettierrc.json`) — check with `pnpm prettier`, fix with `pnpm prettier-fix`
- **pre-commit** hooks enforce checks on commit (detect-secrets, check-yaml, eslint, prettier)
- Direct commits to `main`/`master` and `release/*` branches are blocked by pre-commit

## Testing

- **Jest** (`^30.4.2`) with `ts-jest` for CDK infrastructure tests
- CDK tests live in `./test/` and validate stacks against `cdk-nag` rules
- Python lambda tests live alongside source in `tests/` subdirectories (run via `make test`)

## TypeScript Config Highlights

- `strict: true`, `noImplicitAny: true`, `strictNullChecks: true`
- `noImplicitReturns: true`
- `resolveJsonModule: true` (JSON imports allowed)
- `skipLibCheck: true`

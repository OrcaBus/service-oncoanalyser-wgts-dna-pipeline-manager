.PHONY: test deep scan

check:
	@pnpm audit
	@pnpm prettier
	@pnpm lint
	@pre-commit run --all-files

fix:
	@pnpm prettier-fix
	@pnpm lint-fix

fix-all: fix
	@(cd app && make fix)

install:
	@pnpm install --frozen-lockfile

test:
	@pnpm test

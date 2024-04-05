# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Project renamed from **pydantic-plus** to **nested-config**

### Added

- Can find paths to other config files and parse them using their respective Pydantic
  models (this is the main functionality now).
- Pydantic 2.0 compatibility.
- New simple function to parse any kind of config file, not just TOML.
- Validators for `PurePath` and `PureWindowsPath`
- Simplify JSON encoder specification to work for all `PurePaths`
- pytest and mypy checks, checked with GitLab CI/CD

## [1.1.3] - 2021-07-30

- Add README
- Simplify PurePosixPath validator
- Export `TomlParsingError` from rtoml for downstream exception handling (without needing to explicitly
  import rtoml).

[Unreleased]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v1.1.3...master
[1.1.3]: https://gitlab.com/osu-nrsg/nested-config/-/tags/v1.1.3

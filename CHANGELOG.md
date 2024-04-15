# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.3] - 2024-04-15

- Fix typing issue regression for Pydantic < 2.0 introduced in last release
- Move package to `src` directory

## [2.0.2] - 2024-04-12

- Generalize handling of lists and dicts such that if the source config value and the
  model annotation are both lists, recursively evaluate each item. This addresses the
  situation where there may be a dict in the source config that corresponds to a Pydantic
  model and that dict contains paths to other configs.

## [2.0.1] - 2024-04-10

- Make dependency specifications more generous
- Use `yaml.safe_load`
- Test minimum dependency versions in CI

## [2.0.0] - 2024-04-09

### Changed

- Project renamed from **pydantic-plus** to **nested-config**

### Added

- Can find paths to other config files and parse them using their respective Pydantic
  models using `validate_config` or `BaseModel` (this is the main functionality now).
- Pydantic 2.0 compatibility.
- Can validate any config file. TOML and JSON built in, YAML optional, others can be
  added.
- Validators for `PurePath` and `PureWindowsPath`
- Simplify JSON encoder specification to work for all `PurePaths`
- pytest and mypy checks, checked with GitLab CI/CD

## [1.1.3] - 2021-07-30

- Add README
- Simplify PurePosixPath validator
- Export `TomlParsingError` from rtoml for downstream exception handling (without needing to explicitly
  import rtoml).

[Unreleased]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.3...master
[2.0.3]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.2...v2.0.3
[2.0.2]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.1...v2.0.2
[2.0.1]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.0...v2.0.1
[2.0.0]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v1.1.3...v2.0.0
[1.1.3]: https://gitlab.com/osu-nrsg/nested-config/-/tags/v1.1.3

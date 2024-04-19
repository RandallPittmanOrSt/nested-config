# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2024-04-19

- Fixed problem where `expand_config` didn't work with PEP 563 stringized annotations. Now
  using `typing.get_type_hints` rather than directly querying `__annotations__`.
- Added test with `from __future__ import annotations`

## [2.1.1] - 2024-04-19

- Export ConfigExpansionError in `__init__.py`
- Fix/update docstrings

## [2.1.0] - 2024-04-18

### Added

- `nested_config.expand_config` - Recursively read in any config file(s) into a dict based
  on model class(es). This is now the primary functionality, superseeding
  `validate_config`, which will be deprecated.

### Changed

- Pydantic is now an extra (optional) dependency, only needed to use the below [deprecated
  syntax](#2.1.0-deprecated). All Pydantic stuff has been merged into a single module and
  emits deprecation warnings when used.
- Improved deb build and test scripts

### Deprecated <a name="2.1.0-deprecated"></a>

- Pydantic PurePath validator and JSON encoder -- Doesn't need to be part of this project
  and not needed in Pydantic 2+
- Pydantic validation integration -- This project started out as being specifically for
  working with Pydantic models and was tightly integrated with Pydantic, but that is no
  longer necessary. Use with Pydantic or attrs or whatever is better left to the user.

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

[Unreleased]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.1.2...master
[2.1.2]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.1.1...v2.1.2
[2.1.1]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.1.0...v2.1.1
[2.1.0]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.3...v2.1.0
[2.0.3]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.2...v2.0.3
[2.0.2]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.1...v2.0.2
[2.0.1]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v2.0.0...v2.0.1
[2.0.0]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v1.1.3...v2.0.0
[1.1.3]: https://gitlab.com/osu-nrsg/nested-config/-/tags/v1.1.3

# TEST-TRAIN-CONTRACT-077-085 — Evidência de Execução
- Data: 2026-03-02
- Status: FAIL
- Comando: pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v
- AR Origem: AR_200

## Output pytest

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0 -- C:\HB TRACK\Hb Track - Backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\HB TRACK\Hb Track - Backend
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.0, hypothesis-6.151.9, asyncio-1.3.0, cov-7.0.0, schemathesis-4.10.2
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 20 items

tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_router_file_exists FAILED [  5%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_router_prefix_is_alerts_suggestions FAILED [ 10%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_get_alerts_team_active_route_defined FAILED [ 15%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_get_alerts_team_active_is_get_method FAILED [ 20%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain078AlertsTeamHistory::test_get_alerts_team_history_route_defined FAILED [ 25%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain078AlertsTeamHistory::test_get_alerts_team_history_is_get_method FAILED [ 30%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain079AlertsTeamStats::test_get_alerts_team_stats_route_defined FAILED [ 35%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain079AlertsTeamStats::test_get_alerts_team_stats_is_get_method FAILED [ 40%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain080AlertsDismiss::test_post_alerts_dismiss_route_defined FAILED [ 45%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain080AlertsDismiss::test_post_alerts_dismiss_is_post_method FAILED [ 50%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain081SuggestionsTeamPending::test_get_suggestions_team_pending_route_defined FAILED [ 55%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain081SuggestionsTeamPending::test_get_suggestions_team_pending_is_get_method FAILED [ 60%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain082SuggestionsTeamHistory::test_get_suggestions_team_history_route_defined FAILED [ 65%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain082SuggestionsTeamHistory::test_get_suggestions_team_history_is_get_method FAILED [ 70%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain083SuggestionsTeamStats::test_get_suggestions_team_stats_route_defined FAILED [ 75%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain083SuggestionsTeamStats::test_get_suggestions_team_stats_is_get_method FAILED [ 80%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain084SuggestionsApply::test_post_suggestions_apply_route_defined FAILED [ 85%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain084SuggestionsApply::test_post_suggestions_apply_is_post_method FAILED [ 90%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain085SuggestionsDismiss::test_post_suggestions_dismiss_route_defined FAILED [ 95%]
tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain085SuggestionsDismiss::test_post_suggestions_dismiss_is_post_method FAILED [100%]

================================== FAILURES ===================================
________ TestContractTrain077AlertsTeamActive.test_router_file_exists _________
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:42: in test_router_file_exists
    assert ROUTER_PATH.exists(), f"Router não encontrado: {ROUTER_PATH}"
E   AssertionError: Router não encontrado: C:\HB TRACK\Hb Track - Backend\tests\app\api\v1\routers\training_alerts_step18.py
E   assert False
E    +  where False = exists()
E    +    where exists = WindowsPath('C:/HB TRACK/Hb Track - Backend/tests/app/api/v1/routers/training_alerts_step18.py').exists
_ TestContractTrain077AlertsTeamActive.test_router_prefix_is_alerts_suggestions _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:46: in test_router_prefix_is_alerts_suggestions
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain077AlertsTeamActive.test_get_alerts_team_active_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:53: in test_get_alerts_team_active_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain077AlertsTeamActive.test_get_alerts_team_active_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:60: in test_get_alerts_team_active_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain078AlertsTeamHistory.test_get_alerts_team_history_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:75: in test_get_alerts_team_history_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain078AlertsTeamHistory.test_get_alerts_team_history_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:82: in test_get_alerts_team_history_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain079AlertsTeamStats.test_get_alerts_team_stats_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:97: in test_get_alerts_team_stats_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain079AlertsTeamStats.test_get_alerts_team_stats_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:104: in test_get_alerts_team_stats_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
__ TestContractTrain080AlertsDismiss.test_post_alerts_dismiss_route_defined ___
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:119: in test_post_alerts_dismiss_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
__ TestContractTrain080AlertsDismiss.test_post_alerts_dismiss_is_post_method __
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:126: in test_post_alerts_dismiss_is_post_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain081SuggestionsTeamPending.test_get_suggestions_team_pending_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:141: in test_get_suggestions_team_pending_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain081SuggestionsTeamPending.test_get_suggestions_team_pending_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:148: in test_get_suggestions_team_pending_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain082SuggestionsTeamHistory.test_get_suggestions_team_history_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:163: in test_get_suggestions_team_history_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain082SuggestionsTeamHistory.test_get_suggestions_team_history_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:170: in test_get_suggestions_team_history_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain083SuggestionsTeamStats.test_get_suggestions_team_stats_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:185: in test_get_suggestions_team_stats_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain083SuggestionsTeamStats.test_get_suggestions_team_stats_is_get_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:192: in test_get_suggestions_team_stats_is_get_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain084SuggestionsApply.test_post_suggestions_apply_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:207: in test_post_suggestions_apply_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain084SuggestionsApply.test_post_suggestions_apply_is_post_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:214: in test_post_suggestions_apply_is_post_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain085SuggestionsDismiss.test_post_suggestions_dismiss_route_defined _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:229: in test_post_suggestions_dismiss_route_defined
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
_ TestContractTrain085SuggestionsDismiss.test_post_suggestions_dismiss_is_post_method _
tests\training\contracts\test_contract_train_077_085_alerts_suggestions.py:236: in test_post_suggestions_dismiss_is_post_method
    content = ROUTER_PATH.read_text(encoding="utf-8")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Lib\pathlib.py:1044: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\HB TRACK\\Hb Track - Backend\\tests\\app\\api\\v1\\routers\\training_alerts_step18.py'
============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\config\__init__.py:1303
  C:\HB TRACK\Hb Track - Backend\.venv\Lib\site-packages\_pytest\config\__init__.py:1303: PytestAssertRewriteWarning: Module already imported so cannot be rewritten; anyio
    self._mark_plugins_for_rewrite(hook, disable_autoload)

app\main.py:23
app\main.py:23
app\main.py:23
app\main.py:23
app\main.py:23
app\main.py:23
app\main.py:23
  C:\HB TRACK\Hb Track - Backend\app\main.py:23: DeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.
    from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError, ConflictError

app\schemas\training_alerts_step18.py:27
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:27: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionCreate(BaseModel):

app\schemas\training_alerts_step18.py:49
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:49: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionApply(BaseModel):

app\schemas\training_alerts_step18.py:69
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:69: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionDismiss(BaseModel):

app\schemas\training_alerts_step18.py:81
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:81: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionResponse(BaseModel):

app\schemas\training_alerts_step18.py:126
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:126: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionListResponse(BaseModel):

app\schemas\training_alerts_step18.py:146
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:146: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionStatsResponse(BaseModel):

app\schemas\training_alerts_step18.py:173
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts_step18.py:173: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SuggestionFilters(BaseModel):

app\schemas\person.py:275
  C:\HB TRACK\Hb Track - Backend\app\schemas\person.py:275: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PersonResponse(PersonBase, BaseResponseSchema, SoftDeleteMixin):

app\schemas\person.py:298
  C:\HB TRACK\Hb Track - Backend\app\schemas\person.py:298: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PersonListResponse(BaseModel):

app\schemas\intake\ficha_unica.py:457
  C:\HB TRACK\Hb Track - Backend\app\schemas\intake\ficha_unica.py:457: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class FichaUnicaResponse(BaseModel):

app\schemas\intake\ficha_unica.py:551
  C:\HB TRACK\Hb Track - Backend\app\schemas\intake\ficha_unica.py:551: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class OrganizationAutocompleteItem(BaseModel):

app\schemas\intake\ficha_unica.py:567
  C:\HB TRACK\Hb Track - Backend\app\schemas\intake\ficha_unica.py:567: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class TeamAutocompleteItem(BaseModel):

app\api\v1\routers\lookup.py:29
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:29: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PositionResponse(BaseModel):

app\api\v1\routers\lookup.py:37
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:37: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class CategoryResponse(BaseModel):

app\api\v1\routers\lookup.py:47
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:47: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SchoolingLevelResponse(BaseModel):

app\api\v1\routers\lookup.py:54
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:54: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class OrganizationResponse(BaseModel):

app\api\v1\routers\lookup.py:61
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:61: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class TeamResponse(BaseModel):

app\api\v1\routers\lookup.py:71
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\lookup.py:71: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class SeasonResponse(BaseModel):

app\api\v1\routers\media.py:37
  C:\HB TRACK\Hb Track - Backend\app\api\v1\routers\media.py:37: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class CloudinarySignatureResponse(BaseModel):

app\schemas\exercise_tags.py:19
  C:\HB TRACK\Hb Track - Backend\app\schemas\exercise_tags.py:19: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExerciseTagResponse(ExerciseTagBase):

app\schemas\exercise_tags.py:29
  C:\HB TRACK\Hb Track - Backend\app\schemas\exercise_tags.py:29: PydanticDeprecatedSince20: The `update_forward_refs` method is deprecated; use `model_rebuild` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    ExerciseTagResponse.update_forward_refs()

app\schemas\exercises.py:38
  C:\HB TRACK\Hb Track - Backend\app\schemas\exercises.py:38: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExerciseResponse(ExerciseBase):

app\schemas\exercises.py:58
  C:\HB TRACK\Hb Track - Backend\app\schemas\exercises.py:58: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExerciseACLResponse(BaseModel):

app\schemas\exercise_favorites.py:8
  C:\HB TRACK\Hb Track - Backend\app\schemas\exercise_favorites.py:8: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExerciseFavoriteResponse(BaseModel):

app\schemas\athletes_v2.py:198
  C:\HB TRACK\Hb Track - Backend\app\schemas\athletes_v2.py:198: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AthleteResponse(BaseModel):

app\schemas\athletes_v2.py:279
  C:\HB TRACK\Hb Track - Backend\app\schemas\athletes_v2.py:279: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AthleteStateHistoryResponse(BaseModel):

app\schemas\training_alerts.py:26
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:26: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertCreate(BaseModel):

app\schemas\training_alerts.py:51
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:51: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertUpdate(BaseModel):

app\schemas\training_alerts.py:63
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:63: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertResponse(BaseModel):

app\schemas\training_alerts.py:104
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:104: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertListResponse(BaseModel):

app\schemas\training_alerts.py:124
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:124: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertStatsResponse(BaseModel):

app\schemas\training_alerts.py:151
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_alerts.py:151: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AlertFilters(BaseModel):

app\schemas\training_analytics.py:54
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_analytics.py:54: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class TeamSummaryResponse(BaseModel):

app\schemas\training_analytics.py:95
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_analytics.py:95: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WeeklyLoadResponse(BaseModel):

app\schemas\training_analytics.py:131
  C:\HB TRACK\Hb Track - Backend\app\schemas\training_analytics.py:131: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class DeviationAnalysisResponse(BaseModel):

app\schemas\dashboard.py:157
  C:\HB TRACK\Hb Track - Backend\app\schemas\dashboard.py:157: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class DashboardSummaryResponse(BaseModel):

app\schemas\exports.py:17
  C:\HB TRACK\Hb Track - Backend\app\schemas\exports.py:17: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AnalyticsPDFExportRequest(BaseModel):

app\schemas\exports.py:46
  C:\HB TRACK\Hb Track - Backend\app\schemas\exports.py:46: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AthleteDataExportRequest(BaseModel):

app\schemas\exports.py:69
  C:\HB TRACK\Hb Track - Backend\app\schemas\exports.py:69: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExportJobResponse(BaseModel):

app\schemas\exports.py:106
  C:\HB TRACK\Hb Track - Backend\app\schemas\exports.py:106: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExportJobListResponse(BaseModel):

app\schemas\exports.py:128
  C:\HB TRACK\Hb Track - Backend\app\schemas\exports.py:128: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExportRateLimitResponse(BaseModel):

app\main.py:316
  C:\HB TRACK\Hb Track - Backend\app\main.py:316: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

.venv\Lib\site-packages\fastapi\applications.py:4576
.venv\Lib\site-packages\fastapi\applications.py:4576
  C:\HB TRACK\Hb Track - Backend\.venv\Lib\site-packages\fastapi\applications.py:4576: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

app\main.py:369
  C:\HB TRACK\Hb Track - Backend\app\main.py:369: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_router_file_exists
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_router_prefix_is_alerts_suggestions
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_get_alerts_team_active_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain077AlertsTeamActive::test_get_alerts_team_active_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain078AlertsTeamHistory::test_get_alerts_team_history_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain078AlertsTeamHistory::test_get_alerts_team_history_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain079AlertsTeamStats::test_get_alerts_team_stats_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain079AlertsTeamStats::test_get_alerts_team_stats_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain080AlertsDismiss::test_post_alerts_dismiss_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain080AlertsDismiss::test_post_alerts_dismiss_is_post_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain081SuggestionsTeamPending::test_get_suggestions_team_pending_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain081SuggestionsTeamPending::test_get_suggestions_team_pending_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain082SuggestionsTeamHistory::test_get_suggestions_team_history_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain082SuggestionsTeamHistory::test_get_suggestions_team_history_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain083SuggestionsTeamStats::test_get_suggestions_team_stats_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain083SuggestionsTeamStats::test_get_suggestions_team_stats_is_get_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain084SuggestionsApply::test_post_suggestions_apply_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain084SuggestionsApply::test_post_suggestions_apply_is_post_method
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain085SuggestionsDismiss::test_post_suggestions_dismiss_route_defined
FAILED tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py::TestContractTrain085SuggestionsDismiss::test_post_suggestions_dismiss_is_post_method
======================= 20 failed, 53 warnings in 1.24s =======================

```

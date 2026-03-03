# TEST-TRAIN-INV-005 — Evidência de Execução
- Data: 2026-03-02
- Status: PASS
- Comando: pytest tests/training/invariants/test_inv_train_005_immutability_60_days.py -v
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
collecting ... collected 6 items

tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_immutability_constant_is_60_days PASSED [ 16%]
tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_session_older_than_60_days_blocks_edit PASSED [ 33%]
tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_session_exactly_60_days_allows_edit PASSED [ 50%]
tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_session_30_days_ago_allows_edit PASSED [ 66%]
tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_session_90_days_ago_blocks_edit PASSED [ 83%]
tests/training/invariants/test_inv_train_005_immutability_60_days.py::TestInvTrain005Immutability60Days::test_immutability_error_message_mentions_60_days PASSED [100%]

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
======================= 6 passed, 53 warnings in 0.34s ========================

```

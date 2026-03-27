"""
CRITICAL: Construction Module Tenant Isolation Tests
=====================================================
These tests verify that DailyReport, ConstructionPhoto, and
ConstructionProgress data is strictly scoped to its originating tenant
schema.  A failure here means one promotora can read, submit, or approve
another promotora's on-site construction reports — a confidential
operational data breach.

Test coverage
-------------
1. TestConstructionIsolation
   1a. test_daily_report_not_visible_in_other_tenant
       ORM-level: DailyReport created in tenant_a is completely invisible
       inside tenant_b's schema context.

   1b. test_submit_report_of_other_tenant_returns_404
       HTTP-level: the submit action correctly enforces tenant boundaries.
       A tenant_b client targeting tenant_a's DailyReport UUID must
       receive 404.

   1c. test_approve_report_of_other_tenant_returns_404
       HTTP-level: the approve action correctly enforces tenant boundaries.
       A tenant_b client targeting a SUBMITTED report from tenant_a must
       receive 404.

   1d. test_construction_photos_isolated_by_schema
       ORM-level: ConstructionPhoto rows created in tenant_a are completely
       invisible when querying from within tenant_b's schema context.

   1e. test_construction_progress_does_not_leak_between_tenants
       ORM-level: ConstructionProgress rows created in tenant_a are
       completely invisible when querying from within tenant_b's schema
       context.

Run:
    pytest tests/tenant_isolation/test_construction_isolation.py -v

CI gate: This test MUST pass before merge.
"""
import pytest
from django_tenants.utils import tenant_context
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Module-level counter — prevents slug / unique-constraint collisions between
# tests in the same run without relying on random data.
# ---------------------------------------------------------------------------
_scaffold_counter = 0


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def _make_project(tenant, name="Test Project"):
    """
    Create a Project and a Building inside the given tenant schema.

    Must be called outside any tenant_context block; opens its own.
    Returns (project, building).
    """
    global _scaffold_counter
    _scaffold_counter += 1

    from apps.projects.models import Project, Building

    slug = f"{name.lower().replace(' ', '-')}-{tenant.schema_name}-{_scaffold_counter}"
    with tenant_context(tenant):
        project = Project.objects.create(
            name=f"{name} {_scaffold_counter}",
            slug=slug,
            status="PLANNING",
        )
        building = Building.objects.create(
            project=project,
            name="Bloco A",
            code="BLK-A",
        )
    return project, building


def _make_report(tenant, project, **kwargs):
    """
    Create a DailyReport inside the given tenant schema.

    ``project`` must already exist inside tenant's schema (created via
    _make_project).  Caller is responsible for providing a ``building``
    kwarg when the unique_together constraint (project, building, date)
    requires it — pass building=None to create a project-level report.

    Must be called outside any tenant_context block; opens its own.
    Returns the DailyReport instance.
    """
    from apps.construction.models import DailyReport

    defaults = dict(
        date="2025-01-15",
        summary="Test work summary",
        progress_pct=30,
        status=DailyReport.STATUS_DRAFT,
    )
    defaults.update(kwargs)
    with tenant_context(tenant):
        return DailyReport.objects.create(project=project, **defaults)


def _make_jwt_for_user(user, schema_name: str) -> str:
    """
    Mint a JWT access token carrying a ``tenant_schema`` claim.
    Mirrors CustomTokenObtainPairSerializer used in production.
    """
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


# ---------------------------------------------------------------------------
# Test Class
# ---------------------------------------------------------------------------

@pytest.mark.isolation
class TestConstructionIsolation:
    """
    Tenant isolation tests for the construction module.

    All five tests are mandatory gates before any merge to main/develop.
    A failure in any of these tests means on-site operational data from
    one promotora is leaking into another promotora's schema — a critical
    confidentiality and data-integrity breach.
    """

    @pytest.mark.django_db(transaction=True)
    def test_daily_report_not_visible_in_other_tenant(
        self, tenant_a, tenant_b
    ):
        """
        A DailyReport created inside tenant_a must not appear when
        querying DailyReport from within tenant_b's schema context.

        Failure here = one promotora can enumerate another's daily site
        progress reports — an operational confidentiality breach.
        """
        from apps.construction.models import DailyReport

        project_a, building_a = _make_project(tenant_a, name="Obra Alpha")

        with tenant_context(tenant_a):
            DailyReport.objects.create(
                project=project_a,
                building=building_a,
                date="2025-01-15",
                summary="Test work in tenant A",
                progress_pct=30,
                status=DailyReport.STATUS_DRAFT,
            )
            count_a = DailyReport.objects.count()

        with tenant_context(tenant_b):
            count_b = DailyReport.objects.count()

        assert count_a == 1, (
            f"Sanity check failed: expected 1 DailyReport in tenant_a, "
            f"got {count_a}."
        )
        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} DailyReport(s) "
            f"from tenant_a. Expected 0. On-site reports are leaking "
            f"across the schema boundary."
        )

    @pytest.mark.django_db(transaction=True)
    def test_submit_report_of_other_tenant_returns_404(
        self,
        tenant_a,
        tenant_b,
        api_client_tenant_a,
        api_client_tenant_b,
        user_tenant_a,
    ):
        """
        A tenant_b client that knows the UUID of tenant_a's DailyReport
        and POSTs to the submit action on tenant_b's domain must receive 404.

        The django-tenants schema boundary makes tenant_a's rows invisible
        inside tenant_b's schema, so the router cannot resolve the pk and
        DRF returns 404 — not 403.

        We first verify the endpoint works for the owning tenant (positive
        control), then confirm it is unreachable cross-tenant.
        """
        from apps.construction.models import DailyReport

        project_a, building_a = _make_project(tenant_a, name="Obra Beta")

        with tenant_context(tenant_a):
            report_a = DailyReport.objects.create(
                project=project_a,
                building=building_a,
                date="2025-02-10",
                summary="Daily summary for submit isolation test",
                progress_pct=45,
                status=DailyReport.STATUS_DRAFT,
            )
            report_a_id = report_a.id

        # Positive control: tenant_a can submit their own report.
        response_owner = api_client_tenant_a.post(
            f"/api/v1/construction/daily-reports/{report_a_id}/submit/",
            format="json",
        )
        # Accept 200 (success) or 400 (business rule violation such as missing
        # required fields) — both mean the endpoint was found and processed.
        # A 404 from the owner would indicate a routing problem unrelated to
        # isolation, which would be a separate bug.
        assert response_owner.status_code != 404, (
            f"Positive control failed: tenant_a owner received 404 when "
            f"submitting their own report {report_a_id}. "
            f"Got {response_owner.status_code}. "
            f"Check construction URL routing before investigating isolation."
        )

        # Isolation check: tenant_b must not be able to reach the same UUID.
        response_cross = api_client_tenant_b.post(
            f"/api/v1/construction/daily-reports/{report_a_id}/submit/",
            format="json",
        )
        assert response_cross.status_code == 404, (
            f"ISOLATION BREACH: tenant_b client received "
            f"{response_cross.status_code} when submitting tenant_a's "
            f"DailyReport {report_a_id} via tenant_b's domain. "
            f"Expected 404 — the UUID must be invisible in tenant_b's schema."
        )

    @pytest.mark.django_db(transaction=True)
    def test_approve_report_of_other_tenant_returns_404(
        self,
        tenant_a,
        tenant_b,
        api_client_tenant_a,
        api_client_tenant_b,
        user_tenant_a,
    ):
        """
        A tenant_b client that knows the UUID of a SUBMITTED DailyReport in
        tenant_a and POSTs to the approve action on tenant_b's domain must
        receive 404.

        Approval is a privileged state transition that, if achievable
        cross-tenant, would let one promotora alter another's workflow state.
        """
        from apps.construction.models import DailyReport

        project_a, building_a = _make_project(tenant_a, name="Obra Gama")

        with tenant_context(tenant_a):
            report_a = DailyReport.objects.create(
                project=project_a,
                building=building_a,
                date="2025-03-05",
                summary="Submitted report for approve isolation test",
                progress_pct=60,
                status=DailyReport.STATUS_SUBMITTED,
            )
            report_a_id = report_a.id

        # Positive control: tenant_a can attempt to approve their own report.
        response_owner = api_client_tenant_a.post(
            f"/api/v1/construction/daily-reports/{report_a_id}/approve/",
            format="json",
        )
        assert response_owner.status_code != 404, (
            f"Positive control failed: tenant_a owner received 404 when "
            f"approving their own report {report_a_id}. "
            f"Got {response_owner.status_code}. "
            f"Check construction URL routing before investigating isolation."
        )

        # Isolation check: tenant_b must not be able to reach the same UUID.
        response_cross = api_client_tenant_b.post(
            f"/api/v1/construction/daily-reports/{report_a_id}/approve/",
            format="json",
        )
        assert response_cross.status_code == 404, (
            f"ISOLATION BREACH: tenant_b client received "
            f"{response_cross.status_code} when approving tenant_a's "
            f"DailyReport {report_a_id} via tenant_b's domain. "
            f"Expected 404 — the UUID must be invisible in tenant_b's schema."
        )

    @pytest.mark.django_db(transaction=True)
    def test_construction_photos_isolated_by_schema(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        ConstructionPhoto rows created in tenant_a (linked to a tenant_a
        DailyReport) must not appear when querying ConstructionPhoto from
        within tenant_b's schema context.

        Failure here = photographic evidence from one construction site is
        visible to a different promotora — both a commercial breach and a
        potential LGPD / Lei n.o 133/V/2019 violation if workers are
        identifiable.
        """
        from apps.construction.models import ConstructionPhoto, DailyReport

        project_a, building_a = _make_project(tenant_a, name="Obra Delta")

        with tenant_context(tenant_a):
            report_a = DailyReport.objects.create(
                project=project_a,
                building=building_a,
                date="2025-04-20",
                summary="Photo isolation test report",
                progress_pct=55,
                status=DailyReport.STATUS_DRAFT,
            )
            # Create 3 photos linked to the report.
            for i in range(1, 4):
                ConstructionPhoto.objects.create(
                    report=report_a,
                    s3_key=f"tenants/empresa-a/construction/2025/04/photo_{i:02d}.jpg",
                    caption=f"Photo {i} — isolation test",
                    created_by=user_tenant_a,
                )
            count_a = ConstructionPhoto.objects.count()

        with tenant_context(tenant_b):
            count_b = ConstructionPhoto.objects.count()

        assert count_a == 3, (
            f"Sanity check failed: expected 3 ConstructionPhoto(s) in "
            f"tenant_a, got {count_a}."
        )
        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} ConstructionPhoto(s) "
            f"from tenant_a. Expected 0. Construction site photographs are "
            f"leaking across the schema boundary."
        )

    @pytest.mark.django_db(transaction=True)
    def test_construction_progress_does_not_leak_between_tenants(
        self, tenant_a, tenant_b
    ):
        """
        ConstructionProgress rows created in tenant_a (aggregated progress
        snapshot for a tenant_a Building) must not appear when querying
        ConstructionProgress from within tenant_b's schema context.

        Failure here = one promotora's aggregated build completion figures
        are visible to a competitor — a commercial confidentiality breach.
        """
        from apps.construction.models import ConstructionProgress, DailyReport

        project_a, building_a = _make_project(tenant_a, name="Obra Epsilon")

        with tenant_context(tenant_a):
            report_a = DailyReport.objects.create(
                project=project_a,
                building=building_a,
                date="2025-05-10",
                summary="Progress isolation test report",
                progress_pct=75,
                status=DailyReport.STATUS_APPROVED,
            )
            ConstructionProgress.objects.create(
                building=building_a,
                progress_pct=75,
                last_report=report_a,
            )
            count_a = ConstructionProgress.objects.count()

        with tenant_context(tenant_b):
            count_b = ConstructionProgress.objects.count()

        assert count_a == 1, (
            f"Sanity check failed: expected 1 ConstructionProgress in "
            f"tenant_a, got {count_a}."
        )
        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} "
            f"ConstructionProgress record(s) from tenant_a. Expected 0. "
            f"Aggregated build progress figures are leaking across the "
            f"schema boundary."
        )

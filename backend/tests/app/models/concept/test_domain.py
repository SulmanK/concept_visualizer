"""Tests for concept domain models."""

import uuid
from datetime import datetime

from app.models.concept.domain import ColorPalette, ColorVariationCreate, ConceptCreate, ConceptDetail, ConceptSummary


class TestColorPalette:
    """Tests for the ColorPalette domain model."""

    def test_valid_palette(self) -> None:
        """Test creating a valid ColorPalette."""
        palette = ColorPalette(
            name="Vibrant Blue",
            colors=["#0000FF", "#00FFFF", "#000088"],
            description="A vibrant blue color scheme",
            image_url="https://example.com/image.png",
            image_path="user-123/palettes/vibrant-blue.png",
        )
        assert palette.name == "Vibrant Blue"
        assert palette.colors == ["#0000FF", "#00FFFF", "#000088"]
        assert palette.description == "A vibrant blue color scheme"
        assert palette.image_url == "https://example.com/image.png"
        assert palette.image_path == "user-123/palettes/vibrant-blue.png"

    def test_minimal_palette(self) -> None:
        """Test creating a minimal ColorPalette."""
        palette = ColorPalette(name="Minimal", colors=["#000000", "#FFFFFF"], description=None, image_url=None, image_path=None)
        assert palette.name == "Minimal"
        assert palette.colors == ["#000000", "#FFFFFF"]
        assert palette.description is None
        assert palette.image_url is None
        assert palette.image_path is None


class TestConceptSummary:
    """Tests for the ConceptSummary domain model."""

    def test_valid_summary(self) -> None:
        """Test creating a valid ConceptSummary."""
        concept_id = uuid.uuid4()
        now = datetime.now()
        summary = ConceptSummary(
            id=concept_id,
            created_at=now,
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/image.png",
            image_path="user-123/concepts/logo.png",
            color_variations=[
                ColorPalette(
                    name="Blue",
                    colors=["#0000FF", "#00FFFF"],
                    description=None,
                    image_url="https://example.com/var1.png",
                    image_path="user-123/variations/blue.png",
                ),
                ColorPalette(
                    name="Green",
                    colors=["#00FF00", "#88FF88"],
                    description=None,
                    image_url="https://example.com/var2.png",
                    image_path="user-123/variations/green.png",
                ),
            ],
        )
        assert summary.id == concept_id
        assert summary.created_at == now
        assert summary.logo_description == "A modern tech logo"
        assert summary.theme_description == "Blue professional theme"
        assert summary.image_url == "https://example.com/image.png"
        assert summary.image_path == "user-123/concepts/logo.png"
        assert len(summary.color_variations) == 2
        assert summary.color_variations[0].name == "Blue"
        assert summary.color_variations[1].name == "Green"


class TestConceptDetail:
    """Tests for the ConceptDetail domain model."""

    def test_valid_detail(self) -> None:
        """Test creating a valid ConceptDetail."""
        concept_id = uuid.uuid4()
        session_id = uuid.uuid4()
        now = datetime.now()
        detail = ConceptDetail(
            id=concept_id,
            created_at=now,
            session_id=session_id,
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/image.png",
            image_path="user-123/concepts/logo.png",
            color_variations=[
                ColorPalette(
                    name="Blue",
                    colors=["#0000FF", "#00FFFF"],
                    description=None,
                    image_url="https://example.com/var1.png",
                    image_path="user-123/variations/blue.png",
                ),
                ColorPalette(
                    name="Green",
                    colors=["#00FF00", "#88FF88"],
                    description=None,
                    image_url="https://example.com/var2.png",
                    image_path="user-123/variations/green.png",
                ),
            ],
        )
        assert detail.id == concept_id
        assert detail.created_at == now
        assert detail.session_id == session_id
        assert detail.logo_description == "A modern tech logo"
        assert detail.theme_description == "Blue professional theme"
        assert detail.image_url == "https://example.com/image.png"
        assert detail.image_path == "user-123/concepts/logo.png"
        assert len(detail.color_variations) == 2


class TestConceptCreate:
    """Tests for the ConceptCreate domain model."""

    def test_valid_create(self) -> None:
        """Test creating a valid ConceptCreate."""
        session_id = uuid.uuid4()
        create = ConceptCreate(
            session_id=session_id,
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_path="user-123/concepts/logo.png",
            image_url="https://example.com/image.png",
        )
        assert create.session_id == session_id
        assert create.logo_description == "A modern tech logo"
        assert create.theme_description == "Blue professional theme"
        assert create.image_path == "user-123/concepts/logo.png"
        assert create.image_url == "https://example.com/image.png"

    def test_minimal_create(self) -> None:
        """Test creating a minimal ConceptCreate."""
        session_id = uuid.uuid4()
        create = ConceptCreate(
            session_id=session_id,
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_path="user-123/concepts/logo.png",
            image_url=None,
        )
        assert create.session_id == session_id
        assert create.logo_description == "A modern tech logo"
        assert create.theme_description == "Blue professional theme"
        assert create.image_path == "user-123/concepts/logo.png"
        assert create.image_url is None


class TestColorVariationCreate:
    """Tests for the ColorVariationCreate domain model."""

    def test_valid_variation_create(self) -> None:
        """Test creating a valid ColorVariationCreate."""
        concept_id = uuid.uuid4()
        variation = ColorVariationCreate(
            concept_id=concept_id,
            palette_name="Vibrant Blue",
            colors=["#0000FF", "#00FFFF", "#000088"],
            description="A vibrant blue color scheme",
            image_path="user-123/variations/vibrant-blue.png",
            image_url="https://example.com/image.png",
        )
        assert variation.concept_id == concept_id
        assert variation.palette_name == "Vibrant Blue"
        assert variation.colors == ["#0000FF", "#00FFFF", "#000088"]
        assert variation.description == "A vibrant blue color scheme"
        assert variation.image_path == "user-123/variations/vibrant-blue.png"
        assert variation.image_url == "https://example.com/image.png"

    def test_minimal_variation_create(self) -> None:
        """Test creating a minimal ColorVariationCreate."""
        concept_id = uuid.uuid4()
        variation = ColorVariationCreate(
            concept_id=concept_id,
            palette_name="Simple",
            colors=["#000000", "#FFFFFF"],
            description=None,
            image_path="user-123/variations/simple.png",
            image_url=None,
        )
        assert variation.concept_id == concept_id
        assert variation.palette_name == "Simple"
        assert variation.colors == ["#000000", "#FFFFFF"]
        assert variation.description is None
        assert variation.image_path == "user-123/variations/simple.png"
        assert variation.image_url is None

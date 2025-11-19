"""
Unit tests for note service utilities
"""
import pytest
from services.note_service import NoteService


class TestMarkdownRendering:
    """Test markdown rendering functionality"""
    
    def test_render_basic_markdown(self):
        """Test rendering basic markdown"""
        content = "# Heading\n\nParagraph text"
        html = NoteService.render_markdown(content)
        
        assert "<h1>" in html
        assert "Heading" in html
        assert "Paragraph text" in html
    
    def test_render_bold_text(self):
        """Test rendering bold text"""
        content = "**Bold text**"
        html = NoteService.render_markdown(content)
        
        assert "<strong>" in html or "<b>" in html
        assert "Bold text" in html
    
    def test_render_code_block(self):
        """Test rendering code blocks"""
        content = "```python\nprint('hello')\n```"
        html = NoteService.render_markdown(content)
        
        assert "<code>" in html
        assert "print" in html
    
    def test_render_list(self):
        """Test rendering lists"""
        content = "- Item 1\n- Item 2"
        html = NoteService.render_markdown(content)
        
        assert "<li>" in html
        assert "Item 1" in html


class TestPreviewGeneration:
    """Test preview text generation"""
    
    def test_generate_preview_short_text(self):
        """Test preview for short text"""
        content = "Short content"
        preview = NoteService._generate_preview(content)
        
        assert preview == "Short content"
    
    def test_generate_preview_long_text(self):
        """Test preview for long text"""
        content = "A" * 300
        preview = NoteService._generate_preview(content, max_length=200)
        
        assert len(preview) <= 203  # 200 + "..."
        assert preview.endswith("...")
    
    def test_generate_preview_with_query(self):
        """Test preview generation with search query"""
        content = "This is a long text with the word Python somewhere in the middle of it all"
        preview = NoteService._generate_preview(content, query="Python")
        
        assert "Python" in preview
        assert "..." in preview
    
    def test_generate_preview_removes_markdown(self):
        """Test that preview removes markdown formatting"""
        content = "# Heading\n\n**Bold** text with `code`"
        preview = NoteService._generate_preview(content)
        
        assert "#" not in preview
        assert "**" not in preview
        assert "`" not in preview


class TestHighlightExtraction:
    """Test highlight extraction for search results"""
    
    def test_extract_highlights(self):
        """Test extracting highlights from content"""
        content = "First sentence. Second sentence with Python. Third sentence."
        highlights = NoteService._extract_highlights(content, "Python")
        
        assert len(highlights) >= 1
        assert any("Python" in h for h in highlights)
    
    def test_extract_highlights_max_limit(self):
        """Test that highlights are limited"""
        content = "Python here. Python there. Python everywhere. Python again."
        highlights = NoteService._extract_highlights(content, "Python", max_highlights=2)
        
        assert len(highlights) <= 2
    
    def test_extract_highlights_case_insensitive(self):
        """Test case-insensitive highlight extraction"""
        content = "This contains python in lowercase."
        highlights = NoteService._extract_highlights(content, "Python")
        
        assert len(highlights) >= 1
        assert any("python" in h.lower() for h in highlights)

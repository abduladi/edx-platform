"""
Tests for sequence module.
"""
# pylint: disable=no-member
from datetime import timedelta
from django.utils.timezone import now
from freezegun import freeze_time
from mock import Mock
from xmodule.tests import get_test_system
from xmodule.tests.helpers import StubUserService
from xmodule.tests.xml import XModuleXmlImportTest
from xmodule.tests.xml import factories as xml
from xmodule.x_module import STUDENT_VIEW
from xmodule.seq_module import SequenceModule

TODAY = now()
TOMORROW = TODAY + timedelta(days=1)
DAY_AFTER_TOMORROW = TOMORROW + timedelta(days=1)


class SequenceBlockTestBase(XModuleXmlImportTest):
    """
    Base class for tests of Sequence Module.
    """
    @classmethod
    def setUpClass(cls):
        super(SequenceBlockTestBase, cls).setUpClass()

        course_xml = cls._set_up_course_xml()
        cls.course = cls.process_xml(course_xml)
        cls._set_up_module_system(cls.course)

        for chapter_index in range(len(cls.course.get_children())):
            chapter = cls._set_up_block(cls.course, chapter_index)
            setattr(cls, 'chapter_{}'.format(chapter_index + 1), chapter)

            for sequence_index in range(len(chapter.get_children())):
                sequence = cls._set_up_block(chapter, sequence_index)
                setattr(cls, 'sequence_{}_{}'.format(chapter_index + 1, sequence_index + 1), sequence)

    @classmethod
    def _set_up_course_xml(cls):
        """
        Sets up and returns XML course structure.
        """
        course = xml.CourseFactory.build(end=str(TOMORROW))

        chapter_1 = xml.ChapterFactory.build(parent=course)  # has 2 child sequences
        xml.ChapterFactory.build(parent=course)  # has 0 child sequences
        chapter_3 = xml.ChapterFactory.build(parent=course)  # has 1 child sequence
        chapter_4 = xml.ChapterFactory.build(parent=course)  # has 1 child sequence, with hide_after_due

        xml.SequenceFactory.build(parent=chapter_1)
        xml.SequenceFactory.build(parent=chapter_1)
        sequence_3_1 = xml.SequenceFactory.build(parent=chapter_3)  # has 3 verticals
        xml.SequenceFactory.build(  # sequence_4_1
            parent=chapter_4,
            hide_after_due=str(True),
            due=str(TOMORROW),
        )

        for _ in range(3):
            xml.VerticalFactory.build(parent=sequence_3_1)

        return course

    @classmethod
    def _set_up_block(cls, parent, index_in_parent):
        """
        Sets up the stub sequence module for testing.
        """
        block = parent.get_children()[index_in_parent]

        cls._set_up_module_system(block)

        block.xmodule_runtime._services['bookmarks'] = Mock()  # pylint: disable=protected-access
        block.xmodule_runtime._services['user'] = StubUserService()  # pylint: disable=protected-access
        block.xmodule_runtime.xmodule_instance = getattr(block, '_xmodule', None)  # pylint: disable=protected-access
        block.parent = parent.location
        return block

    @classmethod
    def _set_up_module_system(cls, block):
        """
        Sets up the test module system for the given block.
        """
        module_system = get_test_system()
        module_system.descriptor_runtime = block._runtime  # pylint: disable=protected-access
        block.xmodule_runtime = module_system

    def _get_rendered_student_view(self, sequence, requested_child=None, extra_context=None):
        """
        Returns the rendered student view for the given sequence and the
        requested_child parameter.
        """
        context = {'requested_child': requested_child}
        if extra_context:
            context.update(extra_context)
        return sequence.xmodule_runtime.render(sequence, STUDENT_VIEW, context).content

    def _assert_view_at_position(self, rendered_html, expected_position):
        """
        Verifies that the rendered view contains the expected position.
        """
        self.assertIn("'position': {}".format(expected_position), rendered_html)


class SequenceBlockTestCase(SequenceBlockTestBase):
    """
    Concrete class testing sequence module code in an instructor-paced course.
    """
    def test_student_view_init(self):
        seq_module = SequenceModule(runtime=Mock(position=2), descriptor=Mock(), scope_ids=Mock())
        self.assertEquals(seq_module.position, 2)  # matches position set in the runtime

    def test_render_student_view(self):
        html = self._get_rendered_student_view(
            self.sequence_3_1,
            extra_context=dict(next_url='NextSequential', prev_url='PrevSequential'),
        )
        self._assert_view_at_position(html, expected_position=1)
        self.assertIn(unicode(self.sequence_3_1.location), html)
        self.assertIn("'next_url': 'NextSequential'", html)
        self.assertIn("'prev_url': 'PrevSequential'", html)

    def test_student_view_first_child(self):
        html = self._get_rendered_student_view(self.sequence_3_1, requested_child='first')
        self._assert_view_at_position(html, expected_position=1)

    def test_student_view_last_child(self):
        html = self._get_rendered_student_view(self.sequence_3_1, requested_child='last')
        self._assert_view_at_position(html, expected_position=3)

    def test_tooltip(self):
        html = self._get_rendered_student_view(self.sequence_3_1, requested_child=None)
        for child in self.sequence_3_1.children:
            self.assertIn("'page_title': '{}'".format(child.name), html)

    def test_hidden_content_before_due(self):
        html = self._get_rendered_student_view(self.sequence_4_1)
        self.assertIn("seq_module.html", html)
        self.assertIn("'banner_text': None", html)

    @freeze_time(DAY_AFTER_TOMORROW)
    def test_hidden_content_past_due(self):
        progress_url = 'http://test_progress_link'
        html = self._get_rendered_student_view(
            self.sequence_4_1,
            extra_context=dict(progress_url=progress_url),
        )
        self.assertIn("hidden_content.html", html)
        self.assertIn(progress_url, html)

    @freeze_time(DAY_AFTER_TOMORROW)
    def test_masquerade_hidden_content_past_due(self):
        html = self._get_rendered_student_view(
            self.sequence_4_1,
            extra_context=dict(specific_masquerade=True),
        )
        self.assertIn("seq_module.html", html)
        self.assertIn(
            "'banner_text': 'Because the due date has passed, "
            "this assignment is hidden from the learner.'",
            html
        )


class SelfPacedSequenceBlockTestCase(SequenceBlockTestBase):
    """
    Allows tests to be run against a self-paced course.
    """
    def setUp(self, *args, **kwargs):
        """
        Store the previous value of self.course.self_paced, and force the
        effective value to be True for the duration of this test.
        """
        super(SelfPacedSequenceBlockTestCase, self).setUp(*args, **kwargs)
        self.previous_self_paced = self.course.self_paced
        self.course.self_paced = True

    def tearDown(self, *args, **kwargs):
        """
        Restore the previous value of self.course.self_paced after test.
        """
        self.course.self_paced = self.previous_self_paced
        super(SelfPacedSequenceBlockTestCase, self).tearDown(*args, **kwargs)

    @freeze_time(DAY_AFTER_TOMORROW)
    def test_hidden_content_past_end(self):
        progress_url = 'http://test_progress_link'
        html = self._get_rendered_student_view(
            self.sequence_4_1,
            extra_context=dict(progress_url=progress_url),
        )
        self.assertIn("hidden_content.html", html)
        self.assertIn(progress_url, html)

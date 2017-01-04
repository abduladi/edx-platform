define(['jquery', 'underscore', 'edx-ui-toolkit/js/utils/spec-helpers/ajax-helpers',
        'common/js/spec_helpers/template_helpers', 'js/views/modals/move_xblock_modal', 'js/models/xblock_info'],
    function($, _, AjaxHelpers, TemplateHelpers, MoveXBlockModal, XBlockInfo) {
        'use strict';
        describe('MoveXBlockModal', function() {
            var modal,
                showModal,
                DISPLAY_NAME = 'HTML 101',
                MOVE_TITLE = 'Move';

            showModal = function() {
                modal = new MoveXBlockModal({
                    sourceXBlockInfo: new XBlockInfo({
                        id: 'testCourse/branch/draft/block/verticalFFF',
                        display_name: DISPLAY_NAME,
                        category: 'html'
                    }),
                    XBlockUrlRoot: '/xblock'
                });
                modal.show();
            };

            beforeEach(function() {
                TemplateHelpers.installTemplates([
                    'basic-modal',
                    'modal-button',
                    'move-xblock-modal'
                ]);
                showModal();
            });

            it('rendered as expected', function() {
                expect(modal.$el.find('.modal-header .title').text()).toEqual(MOVE_TITLE);
                expect(
                    modal.$el.find('.modal-content .source-display-name').text()
                ).toEqual('"' + DISPLAY_NAME + '"');
                expect(modal.$el.find('.modal-actions .action-primary.action-move').text()).toEqual(MOVE_TITLE);
            });
        });
    });

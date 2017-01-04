/**
 * This is a base modal implementation that provides common utilities.
 *
 * A modal implementation should override the following methods:
 *
 *   getTitle():
 *     returns the title for the modal.
 *   getHTMLContent():
 *     returns the HTML content to be shown inside the modal.
 *
 * A modal implementation should also provide the following options:
 *
 *   modalName: A string identifying the modal.
 *   modalType: A string identifying the type of the modal.
 *   modalSize: A string, either 'sm', 'med', or 'lg' indicating the
 *     size of the modal.
 *   viewSpecificClasses: A string of CSS classes to be attached to
 *     the modal window.
 *   addPrimaryActionButton: A boolean indicating whether to include a primary action
 *     button on the modal.
 *   primaryActionButtonType: A string to be used as type for primary action button.
 *   primaryActionButtonTitle: A string to be used as title for primary action button.
 */
define(['jquery', 'underscore', 'gettext', 'js/views/baseview'],
    function($, _, gettext, BaseView) {
        var BaseModal = BaseView.extend({
            tabbable_elements: [
                "a[href]:not([tabindex='-1'])",
                "area[href]:not([tabindex='-1'])",
                "input:not([disabled]):not([tabindex='-1'])",
                "select:not([disabled]):not([tabindex='-1'])",
                "textarea:not([disabled]):not([tabindex='-1'])",
                "button:not([disabled]):not([tabindex='-1'])",
                "iframe:not([tabindex='-1'])",
                "[tabindex]:not([tabindex='-1'])",
                "[contentEditable=true]:not([tabindex='-1'])"
            ],

            events: {
                'click .action-cancel': 'cancel'
            },

            options: _.extend({}, BaseView.prototype.options, {
                type: 'prompt',
                closeIcon: false,
                icon: false,
                modalName: 'basic',
                modalType: 'generic',
                modalSize: 'lg',
                title: '',
                modalWindowClass: '.modal-window',
                // A list of class names, separated by space.
                viewSpecificClasses: '',
                addPrimaryActionButton: true,
                primaryActionButtonType: 'save',
                primaryActionButtonTitle: gettext('Save')
            }),

            initialize: function() {
                var parent = this.options.parent,
                    parentElement = this.options.parentElement;
                this.modalTemplate = this.loadTemplate('basic-modal');
                this.buttonTemplate = this.loadTemplate('modal-button');
                if (parent) {
                    parentElement = parent.$el;
                } else if (!parentElement) {
                    parentElement = this.$el.closest(this.options.modalWindowClass);
                    if (parentElement.length === 0) {
                        parentElement = $('body');
                    }
                }
                this.parentElement = parentElement;
            },

            render: function() {
                this.$el.html(this.modalTemplate({
                    name: this.options.modalName,
                    type: this.options.modalType,
                    size: this.options.modalSize,
                    title: this.getTitle(),
                    viewSpecificClasses: this.options.viewSpecificClasses
                }));
                this.addActionButtons();
                this.renderContents();
                this.parentElement.append(this.$el);
            },

            getTitle: function() {
                return this.options.title;
            },

            renderContents: function() {
                var contentHtml = this.getContentHtml();
                this.$('.modal-content').html(contentHtml);
            },

            /**
             * Returns the content to be shown in the modal.
             */
            getContentHtml: function() {
                return '';
            },

            inFocus: function() {
                var tabbables;
                // element to send focus to on hide
                this.options.outFocusElement = this.options.outFocusElement || document.activeElement;

                // Set focus to the container.
                this.$(this.options.modalWindowClass).first().focus();

                // Make tabs within the prompt loop rather than setting focus
                // back to the main content of the page.
                tabbables = this.$(this.tabbable_elements.join());
                tabbables.on('keydown', function(event) {
                    // On tab backward from the first tabbable item in the prompt
                    if (event.which === 9 && event.shiftKey && event.target === tabbables.first()[0]) {
                        event.preventDefault();
                        tabbables.last().focus();
                    // On tab forward from the last tabbable item in the prompt
                    } else if (event.which === 9 && !event.shiftKey && event.target === tabbables.last()[0]) {
                        event.preventDefault();
                        tabbables.first().focus();
                    }
                });
            },

            outFocus: function() {
                this.$(this.tabbable_elements.join()).off('keydown');
                if (this.options.outFocusElement) {
                    this.options.outFocusElement.focus();
                }
            },

            show: function() {
                this.render();
                this.resize();
                $(window).resize(_.bind(this.resize, this));

                // after showing and resizing, send focus to firs focusable element
                this.inFocus();
            },

            hide: function() {
                // Completely remove the modal from the DOM
                this.undelegateEvents();
                this.$el.html('');
                this.outFocus();
            },

            cancel: function(event) {
                if (event) {
                    event.preventDefault();
                    event.stopPropagation(); // Make sure parent modals don't see the click
                }
                this.hide();
            },

            /**
             * Adds the action buttons to the modal.
             */
            addActionButtons: function() {
                if (this.options.addPrimaryActionButton) {
                    this.addActionButton(
                        this.options.primaryActionButtonType,
                        this.options.primaryActionButtonTitle,
                        true
                    );
                }
                this.addActionButton('cancel', gettext('Cancel'));
            },

            /**
             * Adds a new action button to the modal.
             * @param type The type of the action.
             * @param name The action's name.
             * @param isPrimary True if this button is the primary one.
             */
            addActionButton: function(type, name, isPrimary) {
                var html = this.buttonTemplate({
                    type: type,
                    name: name,
                    isPrimary: isPrimary
                });
                this.getActionBar().find('ul').append(html);
            },

            /**
             * Returns the action bar that contains the modal's action buttons.
             */
            getActionBar: function() {
                return this.$(this.options.modalWindowClass + ' > div > .modal-actions');
            },

            /**
             * Returns the action button of the specified type.
             */
            getActionButton: function(type) {
                return this.getActionBar().find('.action-' + type);
            },

            enableActionButton: function(type) {
                this.getActionBar().find('.action-' + type).prop('disabled', false).removeClass('is-disabled');
            },

            disableActionButton: function(type) {
                this.getActionBar().find('.action-' + type).prop('disabled', true).addClass('is-disabled');
            },

            resize: function() {
                var top, left, modalWindow, modalWidth, modalHeight,
                    availableWidth, availableHeight, maxWidth, maxHeight;

                modalWindow = this.$el.find(this.options.modalWindowClass);
                availableWidth = $(window).width();
                availableHeight = $(window).height();
                maxWidth = availableWidth * 0.80;
                maxHeight = availableHeight * 0.80;
                modalWidth = Math.min(modalWindow.outerWidth(), maxWidth);
                modalHeight = Math.min(modalWindow.outerHeight(), maxHeight);

                left = (availableWidth - modalWidth) / 2;
                top = (availableHeight - modalHeight) / 2;

                modalWindow.css({
                    top: top + $(window).scrollTop(),
                    left: left + $(window).scrollLeft()
                });
            }
        });

        return BaseModal;
    });

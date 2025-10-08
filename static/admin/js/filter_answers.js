(function($) {
    'use strict';
    
    console.log('🔥 Filter Answers Script Loaded');
    
    $(document).ready(function() {
        
        function setupFiltering() {
            // Find all inline forms
            $('div[id*="productquestionanswer_set"]').each(function() {
                const $row = $(this);
                
                // Find question select (autocomplete creates a hidden select + visible select2)
                const $questionSelect = $row.find('select[name*="-question"]');
                const $answersSelect = $row.find('select[name*="-answers"]');
                
                if ($questionSelect.length && $answersSelect.length) {
                    console.log('✅ Found question and answers fields in row');
                    
                    // Listen for question change
                    $questionSelect.on('change', function() {
                        const questionId = $(this).val();
                        console.log('📝 Question changed to:', questionId);
                        
                        if (!questionId) {
                            console.log('⚠️ No question selected');
                            return;
                        }
                        
                        // Make AJAX call
                        $.ajax({
                            url: '/admin/get-answers-by-question/',
                            method: 'GET',
                            data: { question_id: questionId },
                            success: function(response) {
                                console.log('✅ Got response:', response);
                                
                                if (response.answer_ids) {
                                    // Clear current selection
                                    $answersSelect.val(null);
                                    
                                    // Get all options
                                    $answersSelect.find('option').each(function() {
                                        const optionValue = $(this).val();
                                        
                                        if (!optionValue) return; // Skip empty option
                                        
                                        // Show/hide based on whether it's in the allowed list
                                        if (response.answer_ids.includes(parseInt(optionValue))) {
                                            $(this).show();
                                        } else {
                                            $(this).hide();
                                        }
                                    });
                                    
                                    // Trigger Select2 update if it exists
                                    if ($answersSelect.hasClass('select2-hidden-accessible')) {
                                        $answersSelect.trigger('change.select2');
                                    }
                                    
                                    console.log('✅ Filtered answers updated');
                                }
                            },
                            error: function(xhr, status, error) {
                                console.error('❌ AJAX Error:', error);
                                console.error('Response:', xhr.responseText);
                            }
                        });
                    });
                    
                    // Trigger initial filter if question already selected
                    if ($questionSelect.val()) {
                        console.log('🔄 Triggering initial filter');
                        $questionSelect.trigger('change');
                    }
                }
            });
        }
        
        // Initial setup
        setTimeout(function() {
            console.log('🚀 Setting up filtering...');
            setupFiltering();
        }, 1000);
        
        // Re-setup when new inline form is added
        $(document).on('formset:added', function(event, $row) {
            console.log('➕ New inline row added');
            setTimeout(setupFiltering, 500);
        });
    });
    
})(django.jQuery || jQuery || $);
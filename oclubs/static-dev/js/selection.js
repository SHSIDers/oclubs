(function($) {
  $(document)
    .ready(function() {

      $('select').select2({});

      function toggle_dateselectionform() {
        if ($('#date_options').val() == 'singledate') {
          $('#date_select_start_div').show();
          $('#date_select_end_div').hide();
        } else if ($('#date_options').val() == 'daterange') {
          $('#date_select_start_div').show();
          $('#date_select_end_div').show();
        } else {
          $('#date_select_start_div').hide();
          $('#date_select_end_div').hide();
        }
      }

      toggle_dateselectionform();

      $('#date_options').on('change', function() {
        toggle_dateselectionform();
      });

    });
}(jQuery));
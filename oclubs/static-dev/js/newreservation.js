(function($) {
  $(document)
    .ready(function() {

      function ajax_request_for_free_classrooms() {
        $.ajax({
          url: $('body').data('updateurl'),
          data: $('#new_reservation').serialize(),
          type: 'POST',
          success: function(selectOptions) {
            $('#free_classrooms').empty();
            for (var i = 0; i < selectOptions.length; i++) {
              $('#free_classrooms').append(
                $("<option></option>")
                .attr("value", selectOptions[i][0])
                .text(selectOptions[i][1])
              );
            }
          }
        });
      }

      $(document).ajaxStart(function() {
        $('.loading_gif').show();
        $('.finished_loading').hide();
      });

      $(document).ajaxStop(function() {
        $('.loading_gif').hide();
        $('.finished_loading').show();

        date = new Date();

        function today() {
          return date.getFullYear() + "-" + (((date.getMonth() + 1) < 10) ? "0" : "") + (date.getMonth() + 1) + "-" + ((date.getDate() < 10) ? "0" : "") + date.getDate();
        };

        function timeNow() {
          return ((date.getHours() < 10) ? "0" : "") + ((date.getHours() > 12) ? (date.getHours() - 12) : date.getHours()) + ":" + ((date.getMinutes() < 10) ? "0" : "") + date.getMinutes() + ":" + ((date.getSeconds() < 10) ? "0" : "") + date.getSeconds() + ((date.getHours() > 12) ? (' PM') : ' AM');
        };

        $('.finished_loading').html(
          '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> &nbsp;&nbsp; Last updated: ' +
          today() + " @ " + timeNow() +
          '&nbsp; &nbsp; <button type="button" class="btn btn-default btn-xs" id="refresh_classrooms">Refresh</button>'
        );

        $('#refresh_classrooms').click(function(event) {
          ajax_request_for_free_classrooms();
        });

      });

      ajax_request_for_free_classrooms();

      $('#building, #timeslot, #date_selection').on('change', function(event) {
        event.preventDefault();
        ajax_request_for_free_classrooms();
      });

      function toggle_sb_app_desc_div() {
        if ($('#SBNeeded-0').prop('checked')) {
          $('#sb_app_desc_div').show();
        } else if ($('#SBNeeded-1').prop('checked')) {
          $('#sb_app_desc_div').hide();
        }
      }

      toggle_sb_app_desc_div();

      $('#SBNeeded').on('change', function(event) {
        toggle_sb_app_desc_div();
      });

    });
}(jQuery));
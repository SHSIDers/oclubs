(function($) {
  $(document)
    .ready(function() {

      $(document).ajaxStart(function() {
        $('.loading_gif').show();
        $('.finished_loading').hide();
      });

      $(document).ajaxStop(function() {
        $('.loading_gif').hide();
        $('.finished_loading').show();


				Date.prototype.today = function() {
					return this.getFullYear() + "-" + (((this.getMonth() + 1) < 10) ? "0" : "") + (this.getMonth() + 1) + "-" + ((this.getDate() < 10) ? "0" : "") + this.getDate();
				};

				Date.prototype.timeNow = function() {
					return ((this.getHours() < 10) ? "0" : "") + ((this.getHours() > 12) ? (this.getHours() - 12) : this.getHours()) + ":" + ((this.getMinutes() < 10) ? "0" : "") + this.getMinutes() + ":" + ((this.getSeconds() < 10) ? "0" : "") + this.getSeconds() + ((this.getHours() > 12) ? (' PM') : ' AM');
				};

        $('.finished_loading').html(
          '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> &nbsp;&nbsp; Last updated: ' +
					new Date().today() + " @ " + new Date().timeNow() +
					'&nbsp; &nbsp; <button type="button" class="btn btn-default btn-xs" id="refresh_classrooms">Refresh</button>'
        );

				$( '#refresh_classrooms' ).click( function(event) {
					ajax_request_for_free_classrooms();
				});

      });

      ajax_request_for_free_classrooms();

      $('#building, #timeslot, #date_selection').on('change', function(event) {
        event.preventDefault();
        ajax_request_for_free_classrooms();
      });


      toggle_sb_app_desc_div();

      $('#SBNeeded').on('change', function(event) {
        toggle_sb_app_desc_div();
      });

    });
}(jQuery));

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

function toggle_sb_app_desc_div() {
  if ($('#SBNeeded-0').prop('checked')) {
    $('#sb_app_desc_div').show();
  } else if ($('#SBNeeded-1').prop('checked')) {
    $('#sb_app_desc_div').hide();
  }
}

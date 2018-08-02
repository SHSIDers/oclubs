( function( $ ) {
	$( document )
		.ready( function() {

      ajax_request_for_free_classrooms();

			$( '#building, #timeslot, #date_selection' ).on('change', function(event) {
        event.preventDefault();
        ajax_request_for_free_classrooms();
      });

      toggle_sb_app_desc_div();

      $( '#SBNeeded' ).on('change', function(event) {
        toggle_sb_app_desc_div();
      });

		} );
}( jQuery ) );

function ajax_request_for_free_classrooms(){
  $.ajax({
    url: $ ( 'body' ).data('updateurl'),
    data: $( '#new_reservation' ).serialize(),
    type: 'POST',
    success: function(selectOptions){
      $( '#free_classrooms' ).empty();
      for (var i = 0; i < selectOptions.length; i++){
        $( '#free_classrooms' ).append(
          $("<option></option>")
          .attr("value", selectOptions[i][0])
          .text(selectOptions[i][1])
        );
      }
    }
  });
}

function toggle_sb_app_desc_div(){
  if( $('#SBNeeded-0').prop('checked') ){
    $( '#sb_app_desc_div' ).show();
  } else if ( $('#SBNeeded-1').prop('checked') ){
    $( '#sb_app_desc_div' ).hide();
  }
}

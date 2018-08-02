( function( $ ) {
	$( document )
		.ready( function() {

			toggle_date_options_div();

			$( '#viewclassroom_options' ).on('change', function() {
				toggle_date_options_div();
			})

			toggle_dateselectionform();

    	$( '#date_options' ).on('change', function(){
    	   toggle_dateselectionform();
    	})

		} );
}( jQuery ) );


function toggle_date_options_div(){
	if ( $('#viewclassroom_options-0').prop('checked') ){
		$( '#date_options_div' ).hide();
	} else if ( $('#viewclassroom_options-1').prop('checked') ){
		$( '#date_options_div' ).show();
	}
}

function toggle_dateselectionform(){
	if( $('#date_options-5').prop('checked') ){
		$( '#date_select_start' ).show();
		$( '#date_select_end' ).hide();
	} else if( $('#date_options-6').prop('checked') ){
		$( '#date_select_start' ).show();
		$( '#date_select_end' ).show();
	} else {
		$( '#date_select_start' ).hide();
		$( '#date_select_end' ).hide();
	}
}

( function( $ ) {
	$( document )
	.ready( function() {

		$( 'select' ).select2({});

		// toggle_date_options_div();

		// $( '#viewclassroom_options' ).on('change', function() {
		// 	toggle_date_options_div();
		// });

		toggle_dateselectionform();

		$( '#date_options' ).on('change', function(){
			toggle_dateselectionform();
		});

	} );
}( jQuery ) );


// function toggle_date_options_div(){
// 	if ( $('#viewclassroom_options-0').prop('checked') ){
// 		$( '#date_options_div' ).hide();
// 	} else if ( $('#viewclassroom_options-1').prop('checked') ){
// 		$( '#date_options_div' ).show();
// 	}
// }

function toggle_dateselectionform(){
	if( $('#date_options').val() == 'singledate' ){
		$( '#date_select_start_div' ).show();
		$( '#date_select_end_div' ).hide();
	} else if( $('#date_options').val() == 'daterange' ){
		$( '#date_select_start_div' ).show();
		$( '#date_select_end_div' ).show();
	} else {
		$( '#date_select_start_div' ).hide();
		$( '#date_select_end_div' ).hide();
	}
}

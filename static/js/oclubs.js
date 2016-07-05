( function( $ ) {
	$( document )
		.ready( function() {
			$( "#loginModal input[name='hasaccount'][value='1']" )
				.click();
			$( "#loginModal input[name='hasaccount']" )
				.change( function() {
					switch ( $( "#loginModal input[name='hasaccount']:checked" )
						.val() ) {
						case '0':
							$( '#loginModal #loginform' )
								.hide();
							$( '#loginModal #registerform' )
								.show();
							break;
						default:
							$( '#loginModal #loginform' )
								.show();
							$( '#loginModal #registerform' )
								.hide();
							break;
					}
				} );

			$( ".clickable" )
				.click( function() {
					window.document.location = $( this )
						.data( "href" );
				} );

			$( "#updatecheck" )
				.click( function() {
					var checked = $( '#leader_radio input[type=radio]:checked' );
					if ( checked.size() > 0 ) {
						$( ".modal .modal-body" )
							.html( "<p>Your choice is " + checked.val() + ".</p>" );
						$( ".modal .modal-footer" )
							.html( "<button type='button' class='btn btn-default' data-dismiss='modal'>Reselect</button>" +
									"<button type='submit' class='btn btn-primary'>Confirm</button>" );
					} else {
						$( ".modal .modal-body" )
							.html( "<p>Please select one memeber as next club leader!</p>" );
						$( ".modal .modal-footer" )
							.html( "<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>" );
					}
				} );

			$( "#updatequit" )
				.click( function() {
					var selected = $( '.form-group select option:selected' );
					$( ".modal .modal-body" )
						.html( "<p>Your choice is " + selected.text() + ".</p>" );
				} );
		} );
} )( jQuery );

function swing( x ) {
	x.className = 'swing animated';
}

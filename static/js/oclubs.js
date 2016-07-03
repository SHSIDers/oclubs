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
							.html( "<p>" + checked.val() + "</p>" );
					} else {
						$( ".modal .modal-body" )
							.html( "<p>Please select one memeber as next club leader!</p>" );
					}
				} );
		} );
} )( jQuery );

function swing( x ) {
	x.className = 'swing animated';
}

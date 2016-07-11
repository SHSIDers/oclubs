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

			$( ".updatehm " )
				.click( function() {
					var date = $( "#date" ).val();
					var contents = $( "#contents" ).val();
					if ( date !== '' && contents !== '' ) {
						$( "#schedule tbody" )
							.append( "<tr><td>" + date + "</td><td>" + contents + "</td><td><button class='btn btn-primary' id='" + contents + "'>Delete</button></td></tr>");
						$( "#" + contents )
							.click( function() {$( this ).parents("tr").eq(0).remove();});
					}
				} );

			$.post( '/login' , {} )
				.done( function(data) {
					if ( data.loggedin === false && $( ".modal .modal-body div p").last().html() !== "<p style='color:red'>Wrong student ID or password. Please input again</p>" ){
						$( ".modal .modal-body div").append("<p style='color:red'>Wrong student ID or password. Please input again</p>");
					} else if (data.loggedin === true) {
						$( "#loginModal" ).modal('toggle');
					}
			} );
		} );
} )( jQuery );

function swing( x ) {
	x.className = 'swing animated';
}

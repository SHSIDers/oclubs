( function( $ ) {
	$( document )
		.ready( function() {
			$( '.clickable' )
				.click( function() {
					window.document.location = $( this )
						.data( 'href' );
				} );

			$( '#updatecheck' )
				.click( function() {
					var checked = $( '#leader_radio input[type=radio]:checked' );
					if ( checked.size() > 0 ) {
						$( '.modal .modal-body' )
							.html( '<p>Your choice is ' + checked.val() + '.</p>' );
						$( '.modal .modal-footer' )
							.html( '<button type="button" class="btn btn-default" data-dismiss="modal">Reselect</button>' +
								'<input type="submit" class="btn btn-primary" form="leader_radio" name="change_leader" value="Confirm">' );
					} else {
						$( '.modal .modal-body' )
							.html( '<p>Please select one memeber as next club leader!</p>' );
						$( '.modal .modal-footer' )
							.html( '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>' );
					}
				} );

			$( '#updatequit' )
				.click( function() {
					var selected = $( '.form-group select option:selected' );
					if ( selected.size() > 0 ) {
						$( '.modal .modal-body' )
							.html( '<p>Your choice is ' + selected.text() + '.</p>' );
					} else {
						$( '.modal .modal-body' )
							.html( '<p>Please choose the club you want to quit.</p>' );
					}
				} );

			$( '.updatehm' )
				.click( function() {
					var date = $( '#date' )
						.val();
					var contents = $( '#contents' )
						.val();
					if ( date !== '' && contents !== '' ) {
						$( '#schedule tbody' )
							.append( '<tr><td>' + date + '</td><td>' + contents + '</td><td><button class="btn btn-primary" id="' + contents + '">Delete</button></td></tr>' );
						$( '#' + contents )
							.click( function() {
								$( this )
									.parents( 'tr' )
									.eq( 0 )
									.remove();
							} );
					}
				} );

			$( '.refresh' )
				.click( function() {
					location.reload();
				} );

			$( 'form #picture' )
				.change( function() {
					$( 'form #upload_content' )
						.text( $( 'form #picture' )
							.val() );
				} );

			$( 'form #excel' )
				.change( function() {
					$( 'form #upload_content' )
						.text( $( 'form #excel' )
							.val() );
				} );

			if ( /\/change_user_info/.test( window.location.href ) ) {
				var init_view = function( item, content ) {
					item.empty()
						.append( $( '<div class="col-sm-8 content"><p></p></div>' ) )
						.append( $( '<div class="col-sm-4 edit"><a style="cursor:pointer">Edit</a></div>' ) );
					item.find( 'p' )
						.text( content );
					item.find( 'a' )
						.click( function( argument ) {
							init_edit( item, content );
						} );
				};
				var init_edit = function( item, content ) {
					item.empty()
						.append( $( '<div class="col-sm-8 content"><input type="text" class="input_content" name="content"></div>' ) )
						.append( $( '<div class="col-sm-4 edit"><a style="cursor:pointer">Edit</a></div>' ) );
					item.find( 'input.input_content' )
						.attr( 'value', content )
						.focus();
					item.find( '.edit' )
						.empty()
						.append( $( '<button class="btn btn-success"><span class="glyphicon glyphicon-ok"></span></button>' ) )
						.append( $( '<button class="btn btn-danger"><span class="glyphicon glyphicon-remove"></span></button>' ) );
					item.find( '.edit .btn-success' )
						.click( function( argument ) {
							new_content = $( item )
								.find( '.input_content' )
								.val();
							$.post( '/user/change_user_info/submit', {
									userid: $( item )
										.parents( 'tr' )
										.eq( 0 )
										.find( '.userid' )
										.text(),
									type: item.attr( 'property-type' ),
									content: new_content
								} )
								.done( function( data ) {
									if ( data.result == 'success' ) {
										init_view( item, new_content );
									} else {
										init_view( item, content );
										alert( data.result );
									}
								} );
						} );
					item.find( '.edit .btn-danger' )
						.click( function( argument ) {
							init_view( item, content );
						} );
				};
				$( '#admin_user_table td.admin_user_info' )
					.each( function() {
						var item = $( this );
						init_view( item, item.text() );
					} );
			}

			$( '#floatmenu' )
				.click( function() {
					var halfscr = ( document.body.clientWidth / 2 ) + 'px';
					$( '#sidenav, #emptyclose' )
						.css( 'width', halfscr );
					$( '#emptyclose' )
						.css( 'left', halfscr );
					$( '#floatmenu' ).fadeOut();
				} );

			$( '#emptyclose, #closebtn' )
				.click( function() {
					$( '#sidenav, #emptyclose' )
						.css( 'width', '0' );
					$( '#floatmenu' ).fadeIn();
				} );

			$( '.teacher_club .switchmode')
				.click( function() {
					$.post( '/user/switch_mode/submit', {
						club: $( this )
								.parents( 'div' )
								.eq( 0 )
								.find( '.club_callsign' )
								.val()
					} );
				} );
		} );
} )( jQuery );

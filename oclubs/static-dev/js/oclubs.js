( function( $ ) {
	$( document )
		.ready( function() {
			$( '.clickable' )
				.click( function() {
					window.location = $( this )
						.data( 'href' );
				} );

			$( 'tr.clickable > td.clickable-cell' )
				.wrapInner( function() {
					return $( '<a>' )
						.attr( 'href', $( this )
							.parent()
							.data( 'href' )
						);
				} );

			$( 'div.clickable' )
				.wrap( function() {
					return $( '<a>' )
						.attr( 'href', $( this )
							.data( 'href' )
						);
				} );

			$( '#updatecheck' )
				.click( function() {
					var checked = $( '#leader_radio input[type=radio]:checked' );
					if ( checked.size() > 0 ) {
						$( '.modal .modal-body p' )
							.text( 'Your choice is ' + checked.val() + '.' );
						$( '.modal .modal-footer' )
							.html( '<button type="button" class="btn btn-default" data-dismiss="modal">Reselect</button>' +
								'<input type="submit" class="btn btn-primary" form="leader_radio" name="change_leader" value="Confirm">' );
					} else {
						$( '.modal .modal-body p' )
							.text( 'Please select one memeber as next club leader!' );
						$( '.modal .modal-footer' )
							.html( '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>' );
					}
				} );

			$( '#updatequit' )
				.click( function() {
					var selected = $( '.form-group select option:selected' );
					$( '.modal .modal-body p' )
						.text( 'Your choice is ' + selected.text() + '.' );
				} );

			$( '.refresh' )
				.click( function() {
					location.reload();
				} );

			$( 'form #picture, form #excel' )
				.change( function() {
					$( this )
						.closest( 'form' )
						.find( '#upload_content' )
						.text( this.files.length > 1 ? this.files.length + ' files' : $( this )
							.val() );
				} );

			if ( /\/user\/change_info/.test( window.location.href ) ) {
				var init_view = function( item, content ) {
					item.empty()
						.append( $( '<div class="col-sm-8 content"><p></p></div>' ) )
						.append( $( '<div class="col-sm-4 edit"><a class="clickable">Edit</a></div>' ) );
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
						.append( $( '<div class="col-sm-4 edit"><a class="clickable">Edit</a></div>' ) );
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
										.closest( 'tr' )
										.find( '.userid' )
										.text(),
									type: item.data( 'property-type' ),
									content: new_content,
									_csrf_token: $( item )
										.closest( 'table' )
										.data( 'csrf' )
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
					$( '#floatmenu' )
						.fadeOut();
				} );

			$( '#emptyclose, #closebtn' )
				.click( function() {
					$( '#sidenav, #emptyclose' )
						.css( 'width', '0' );
					$( '#floatmenu' )
						.fadeIn();
				} );

			$( '.large_container select.mobileselect' )
				.change( function() {
					window.location = this.value;
				} );
		} );
} )( jQuery );

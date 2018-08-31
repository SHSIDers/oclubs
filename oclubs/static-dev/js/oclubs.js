( function ( $ ) {
	$( document )
		.ready( function () {
			function toggleDayNightBtn( currentClass ) {
				if ( currentClass === 'day-mode' ) {
					$( '.day_night_toggle input' )
						.prop( 'checked', false );
				} else {
					$( '.day_night_toggle input' )
						.prop( 'checked', true );
				}
			}

			function toggleDayNightLogo( currentClass ) {
				if ( currentClass === 'day-mode' ) {
					$( '.logo_img_night' )
						.hide();
					$( '.logo_img_day' )
						.show();
				} else {
					$( '.logo_img_night' )
						.show();
					$( '.logo_img_day' )
						.hide();
				}
			}

			function toggleDayNight() {
				var body = $( 'body' );

				body.toggleClass( 'day-mode night-mode' );

				// save preference to local storage
				// toggle btn
				if ( body.hasClass( 'day-mode' ) ) {
					localStorage.theme = 'day-mode';
					toggleDayNightLogo( 'day-mode' );
				} else if ( body.hasClass( 'night-mode' ) ) {
					localStorage.theme = 'night-mode';
					toggleDayNightLogo( 'night-mode ' );
				}
			}

			if ( localStorage.theme ) {
				if ( localStorage.theme === 'day-mode' ) {
					$( 'body' )
						.removeClass( 'night-mode' );
					$( 'body' )
						.addClass( 'day-mode' );
				} else if ( localStorage.theme === 'night-mode' ) {
					$( 'body' )
						.addClass( 'night-mode' );
					$( 'body' )
						.removeClass( 'day-mode' );
				}
			} else {
				localStorage.theme = 'day-mode';
				$( 'body' )
					.addClass( 'day-mode' );
			}

			toggleDayNightLogo( localStorage.theme );
			toggleDayNightBtn( localStorage.theme );

			$( '.day_night_toggle input' )
				.change( function () {
					toggleDayNight();
				} );

			$( document )
				.on( 'click', '.navbar-collapse.in', function ( e ) {
					if ( $( e.target )
						.is( 'a' ) ) {
						$( this )
							.collapse( 'hide' );
					}
				} );

			$( '[data-toggle="popover"]' )
				.popover( {
					container: 'body',
					html: true
				} );

			$( '.clickable' )
				.click( function () {
					window.location = $( this )
						.data( 'href' );
				} );

			$( 'tr.clickable > td' )
				.wrapInner( function () {
					return $( '<a class="clickable-a">' )
						.attr( 'href', $( this )
							.parent()
							.data( 'href' )
						);
				} );

			$( 'div.clickable' )
				.wrap( function () {
					return $( '<a class="clickable-a">' )
						.attr( 'href', $( this )
							.data( 'href' )
						);
				} );

			$( '#updatecheck' )
				.click( function () {
					event.preventDefault();
					$( '.modal .btn-primary' )
						.hide();
					var checked = $( '#leader_radio input[type=radio]:checked' );
					var label = $( "label[for='" + checked.attr( 'id' ) + "']" );
					if ( checked.size() > 0 ) {
						$( '.modal .modal-body p' )
							.html( 'New leader: ' + label.html() );
						$( '.modal .btn-primary' )
							.show();
					} else {
						$( '.modal .modal-body p' )
							.text( 'No selection made.' );
						$( '.modal .btn-primary' )
							.hide();
					}
				} );

			$( '#updatequit' )
				.click( function () {
					var selectedText = $( '#_clubs option:selected' )
						.text();
					$( '.modal .modal-body p' )
						.text( 'Quit from ' + selectedText + '.' );
					$( '#clubs' )
						.val( $( '#_clubs' )
							.val() );
					$( '#reason' )
						.val( $( '#_reason' )
							.val() );
				} );

			$( '.refresh' )
				.click( function () {
					location.reload();
				} );

			$( 'form #picture, form #excel' )
				.change( function () {
					var files = $( '#picture' )
						.prop( 'files' ),
						filenames = $.map( files, function ( val ) {
							return val.name;
						} ),
						retstr = '<br>';

					for ( var i = 0; i < filenames.length; i++ ) {
						retstr = retstr + filenames[ i ] + '<br>'
					}

					$( this )
						.closest( 'form' )
						.find( '#upload_content' )
						.append( retstr );
				} );

			if ( /\/user\/change_info/.test( window.location.href ) ) {
				var initView, initEdit;
				initView = function ( item, content ) {
					item.empty()
						.append( $( '<div class="col-sm-8 content"><p></p></div>' ) )
						.append( $( '<div class="col-sm-4 edit"><a class="clickable">Edit</a></div>' ) );
					item.find( 'p' )
						.text( content );
					item.find( 'a' )
						.click( function () {
							initEdit( item, content );
						} );
				};
				initEdit = function ( item, content ) {
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
						.click( function () {
							var newContent = $( item )
								.find( '.input_content' )
								.val();
							$.post( '/user/change_user_info/submit', {
									userid: $( item )
										.closest( 'tr' )
										.find( '.userid' )
										.text(),
									type: item.data( 'property-type' ),
									content: newContent,
									_csrf_token: $( item )
										.closest( 'table' )
										.data( 'csrf' )
								} )
								.done( function ( data ) {
									if ( data.result === 'success' ) {
										initView( item, newContent );
									} else {
										initView( item, content );
										alert( data.result );
									}
								} );
						} );
					item.find( '.edit .btn-danger' )
						.click( function () {
							initView( item, content );
						} );
				};
				$( '#admin_user_table td.admin_user_info' )
					.each( function () {
						var item = $( this );
						initView( item, item.text() );
					} );
			}

			$( '#floatmenu' )
				.click( function () {
					var halfscr = ( document.body.clientWidth / 2 ) + 'px';
					$( '#sidenav, #emptyclose' )
						.css( 'width', halfscr );
					$( '#emptyclose' )
						.css( 'left', halfscr );
					$( '#floatmenu' )
						.fadeOut();
				} );

			$( '#emptyclose, #closebtn' )
				.click( function () {
					$( '#sidenav, #emptyclose' )
						.css( 'width', '0' );
					$( '#floatmenu' )
						.fadeIn();
				} );

			$( '.large_container select.mobileselect' )
				.change( function () {
					window.location = this.value;
				} );

			window.onscroll = function () {
				if ( document.body.scrollTop > 400 || document.documentElement.scrollTop > 400 ) {
					document.getElementById( 'scroll_to_top_btn' )
						.style.display = 'block';
				} else {
					document.getElementById( 'scroll_to_top_btn' )
						.style.display = 'none';
				}
			};

			$( 'a[href*=\\#]' )
				.on( 'click', function ( event ) {
					event.preventDefault();
					$( 'html, body' )
						.animate( {
							scrollTop: 0
						}, 'slow', function () {} );
				} );

			$( '.homepage_band' )
				.css( 'margin-top', String( window.innerHeight * 0.65 ) + 'px' );
			$( window )
				.on( 'resize', function () {
					$( '.homepage_band' )
						.css( 'margin-top', String( window.innerHeight * 0.65 ) + 'px' );
				} );

			$( '#to_excellentclub' )
				.click( function () {
					$( 'html,body' )
						.animate( {
							scrollTop: $( '#excellentclub' )
								.offset()
								.top - 30
						}, 1000 );
				} );

			$( '.btn_flat' )
				.click( function ( event ) {
					event.preventDefault();
				} );

			// Remove preload class, enable transitions normally
			setTimeout( function () {
				$( 'body' )
					.removeClass( 'preload' );
			}, 2000 );
			$( 'html' )
				.removeClass( 'hidden' );

		} );
}( jQuery ) );

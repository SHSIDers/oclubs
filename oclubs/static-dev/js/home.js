( function ( $ ) {
	$( document )
		.ready( function () {

			$( '#backgroundimg' )
				.attr( 'src', '/static/images/homepagebg.jpg' )
				.on( 'load', function () {
					$( this )
						.remove(); // prevent memory leaks
					$( '#home_body' )
						.css( 'background-image', 'url(/static/images/homepagebg.jpg)' );
					$( '#homepage_block' )
						.css( 'color', '#f8f8f8' );
					$( '#home_navbar a' )
						.css( 'color', '#f8f8f8' );
					$( '#home_navbar .icon-bar' )
						.css( 'background-color', '#f8f8f8' );
					$( '.navbar-brand img' )
						.attr( 'src', '/static/images/logo-night.png' );
				} );

		} );
}( jQuery ) );

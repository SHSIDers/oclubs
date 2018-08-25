( function ( $ ) {
	$( document )
		.ready( function () {

			var $grid = $( '.grid' )
					.masonry( {
					// options
						itemSelector: '.grid-item',
						columnWidth: '.grid-sizer',
						gutter: '.gutter-sizer',
						percentPosition: true,
						stagger: 30
					} ),
				msnry = $grid.data( 'masonry' );

			$grid.imagesLoaded()
				.progress( function () {
					$grid.masonry( 'layout' );
				} );

			$grid.infiniteScroll( {
				// options
				path: '.pagination_next',
				append: '.grid-item',
				outlayer: msnry,
				status: '.page-load-status'
			} );

		} );
}( jQuery ) );

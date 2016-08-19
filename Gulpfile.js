var gulp = require('gulp');
var postcss = require('gulp-postcss');
var cssnano = require('cssnano');
var cssnext = require('postcss-cssnext');
var sorting = require('postcss-sorting');
var stylefmt = require('stylefmt');
var colorguard = require('colorguard');
var jshint = require('gulp-jshint');
var uglify = require('gulp-uglify');
var imagemin = require('gulp-imagemin');
var rename = require('gulp-rename');
var plumber = require('gulp-plumber');

var plumberErrorHandler = {
	errorHandler: function (error) {
        console.log(error.message);
        this.emit('end');
    }
};

gulp.task('styles', function () {
	var build_tasks = [
		cssnext(),
		sorting(),
		cssnano(),
		cssnano(),
		stylefmt(),
	];
	var lint_tasks = [
		// stylelint(),
		colorguard(),
	];
	var minify_tasks = [
		cssnano(),
	];
	return gulp
		.src('./oclubs/static-dev/css/*.css')
		.pipe(plumber(plumberErrorHandler))
		.pipe(postcss(build_tasks))
		.pipe(gulp.dest('./oclubs/static-dev/css-build'))
		.pipe(postcss(lint_tasks))
		.pipe(rename({ suffix: '.min' }))
		// .pipe(cleanCSS())
		.pipe(postcss(minify_tasks))
		.pipe(gulp.dest('./oclubs/static/css'));
});

gulp.task('scripts', function() {
	return gulp
		.src('./oclubs/static-dev/js/*.js')
		.pipe(plumber(plumberErrorHandler))
		.pipe(jshint())
		.pipe(rename({ suffix: '.min' }))
		.pipe(uglify())
		.pipe(gulp.dest('./oclubs/static/js'));
});

gulp.task('images', function() {
	return gulp
		.src('./oclubs/static-dev/images/**')
		.pipe(plumber(plumberErrorHandler))
		.pipe(imagemin())
		.pipe(gulp.dest('./oclubs/static/images'));
});

gulp.task('watch', function() {
	var changeevent = function(event) {
		console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
	};
	gulp.watch('./oclubs/static-dev/css/*.css', ['styles'])
		.on('change', changeevent);
	gulp.watch('./oclubs/static-dev/js/*.js', ['scripts'])
		.on('change', changeevent);
	gulp.watch('./oclubs/static-dev/images/**', ['images'])
		.on('change', changeevent);
});

gulp.task('default', ['styles', 'scripts', 'images', 'watch']);

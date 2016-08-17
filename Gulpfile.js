var gulp = require('gulp');
var compass = require('gulp-compass');
var autoprefixer = require('gulp-autoprefixer');
var cleanCSS = require('gulp-clean-css');
var uglify = require('gulp-uglify');
var imagemin = require('gulp-imagemin');
var rename = require('gulp-rename');
var plumber = require('gulp-plumber');

var compassOptions = {
	sass: './oclubs/static-dev/sass',
	css: './oclubs/static-dev/css',
	images: './oclubs/static/images',
};

var autoprefixerOptions = {
	browsers: [
		'last 2 versions',
		'> 5%',
		'Firefox ESR',

		// https://github.com/twbs/bootstrap-sass#sass-autoprefixer
		'Android 2.3',
		'Android >= 4',
		'Chrome >= 20',
		'Firefox >= 24',
		'Explorer >= 8',
		'iOS >= 6',
		'Opera >= 12',
		'Safari >= 6'
	]
};

var plumberErrorHandler = {
	errorHandler: function (error) {
        console.log(error.message);
        this.emit('end');
    }
};

gulp.task('styles', function () {
	return gulp
		.src('./oclubs/static-dev/sass/*.scss')
		.pipe(plumber(plumberErrorHandler))
		.pipe(compass(compassOptions))
		.pipe(autoprefixer(autoprefixerOptionsZZ))
		.pipe(gulp.dest('./oclubs/static-dev/css'))
		.pipe(rename({ suffix: '.min' }))
		.pipe(cleanCSS())
		.pipe(gulp.dest('./oclubs/static/css'));
});

gulp.task('scripts', function() {
	return gulp
		.src('./oclubs/static-dev/js/*.js')
		.pipe(plumber(plumberErrorHandler))
		.pipe(rename({ suffix: '.min' }))
		.pipe(uglify())
		.pipe(gulp.dest('./oclubs/static/js'));
});

gulp.task('images', function() {
	return gulp
		.src('./oclubs/static-dev/images/*')
		.pipe(plumber(plumberErrorHandler))
		.pipe(imagemin())
		.pipe(gulp.dest('./oclubs/static/images'));
});

gulp.task('watch', function() {
	var changeevent = function(event) {
		console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
	};
	gulp.watch('./oclubs/static-dev/sass/*.scss', ['styles'])
		.on('change', changeevent);
	gulp.watch('./oclubs/static-dev/js/*.js', ['scripts'])
		.on('change', changeevent);
	gulp.watch('./oclubs/static-dev/images/*', ['images'])
		.on('change', changeevent);
});

gulp.task('default', ['styles', 'scripts', 'images', 'watch']);

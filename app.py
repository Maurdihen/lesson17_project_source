# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Int()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Int()

movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()

directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()

@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        director_id_args = request.args.get("director_id")
        genre_id_args = request.args.get("genre_id")
        if genre_id_args and director_id_args:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id_args, Movie.director_id == director_id_args).all()
            return movies_schema.dump(movies), 200
        if genre_id_args:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id_args).all()
            return movies_schema.dump(movies), 200
        if director_id_args:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id_args).all()
            return movies_schema.dump(movies), 200
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200
    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movies_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        if db.session.query(Movie).get(mid):
            movies = db.session.query(Movie).get(mid)
            return movie_schema.dump(movies), 200
        else:
            return "", 404
    def put(self, mid):
        movies = db.session.query(Movie).get(mid)
        req_json = request.json
        movies.title = req_json.get("title")
        movies.description = req_json.get("description")
        movies.trailer = req_json.get("trailer")
        movies.year = req_json.get("year")
        movies.rating = req_json.get("rating")
        db.session.add(movies)
        db.session.commit()
        return "", 204
    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204

@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201

@directors_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        directors = db.session.query(Director).get(did)
        return director_schema.dump(directors), 200
    def put(self, did):
        director = db.session.query(Director).get(did)
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204
    def delete(self, did):
        director = db.session.query(Director).get(did)
        db.session.delete(director)
        db.session.commit()
        return "", 204

@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200
    def post(self):
        req_json = request.json
        new_genre = Director(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genres_ns.route("/<int:gid>")
class GenresView(Resource):
    def get(self, gid):
        genres = db.session.query(Genre, Movie).join(Movie)
        pairs = genres.all()
        res = []
        for pair in pairs:
            if pair[0].id == gid:
                res.append({
                    (pair[0].name): (pair[1].title, pair[1].description, pair[1].trailer, pair[1].year, pair[1].rating)
            })
        return res, 200
    def put(self, gid):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204
    def delete(self, gid):
        genre = db.session.query(Genre).get(gid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(debug=True)

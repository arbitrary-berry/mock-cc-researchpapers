#!/usr/bin/env python3

from flask import Flask, abort, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Research, Author, ResearchAuthors

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)
db.init_app(app)


class Researches(Resource):
    def get(self):
        research_list = [
            research.to_dict(rules=("-research_authors",))
            for research in Research.query.all()
        ]
        return make_response(research_list, 200)


api.add_resource(Researches, "/research")

class ResearchById(Resource):
    def get(self, id):
        research = Research.query.get(id)
        if not research:
            # abort(404, "Research paper not found")
            return make_response({"error": "Research paper not found"}, 404)
        return make_response(
            research.to_dict(
                rules=(
                    "-research_authors",
                    "authors",
                    "-authors.research_authors",
                )
            ),
            200,
        )

    def delete(self, id):
        research = Research.query.get(id)
        if not research:
            return make_response({"error": "Research paper not found"}, 404)
        db.session.delete(research)
        db.session.commit()
        return make_response("", 204)


api.add_resource(ResearchById, "/research/<int:id>")

class Authors(Resource):
    def get(self):
        authors = [
            author.to_dict(
                only=(
                    "id",
                    "name",
                    "field_of_study",
                )
            )
            for author in Author.query.all()
        ]
        return make_response(authors, 200)


api.add_resource(Authors, "/authors")

class ResearchAuthors(Resource):
    def post(self):
        request_data = request.get_json()
        try:
            new_r_author = ResearchAuthor(**request_data)
        except:
            abort(422, errors=["validation errors"])
        db.session.add(new_r_author)
        db.session.commit()
        return make_response(
            new_r_author.author.to_dict(rules=("-research_authors",)), 201
        )

api.add_resource(ResearchAuthors, "/research_author")

if __name__ == '__main__':
    app.run(port=5555, debug=True)

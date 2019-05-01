# -*- coding: utf-8 -*-
from flask.cli import FlaskGroup
from flask_migrate import Migrate, upgrade
from app import db, app

migrate = Migrate(app, db)
cli = FlaskGroup(app)


@app.shell_context_processor
def shell_context():
    return {'app': app, 'db': db}


@cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()


if __name__ == '__main__':
    cli()

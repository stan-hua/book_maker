"""
utils.py

Description:
    Contains helper functions for package
"""

# Non-standard libraries
import jinja2

# Custom libraries
from src.data import constants


################################################################################
#                                  Constants                                   #
################################################################################
# Template cache
CACHE_TEMPLATES = {}


################################################################################
#                               Helper Functions                               #
################################################################################
def render_template(template_fname, template_vars,
                    dir_templates=constants.DIR_TEMPLATES):
    """
    Render JINJA template given its filename and template variables

    Parameters
    ----------
    template_fname : str
        Filename of template
    template_vars : dict
        Contains variables to render in template
    dir_templates : str
        Path to directory containing templates. Defaults to
        constants.DIR_TEMPLATES.

    Returns
    -------
    str
        Rendered template
    """
    # Check if template is in cache
    if template_fname in CACHE_TEMPLATES:
        template = CACHE_TEMPLATES[template_fname]
    else:
        # Set up Environment
        loader = jinja2.FileSystemLoader(dir_templates)
        environment = jinja2.Environment(loader=loader)

        # Create template and cache template
        template = environment.get_template(template_fname)
        CACHE_TEMPLATES[template_fname] = template

    # Render template
    rendered_template = template.render(template_vars)

    return rendered_template

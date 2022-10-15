import re
import xml.etree.ElementTree as etree
import xml.etree.ElementTree as ET
from functools import partial
from typing import Tuple

import favicon
import markdown
import requests
import streamlit as st
from htbuilder import a, img, span
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from streamlit_extras.colored_header import ST_COLOR_PALETTE
from validators import url as validate_url


def css(css: str):
    st.write("<style>" + css + "</style>", unsafe_allow_html=True)


css(
    """
a:hover {
    background-color: rgba(.7, .7, .7, .05);
}
"""
)


def md(text: str, extensions: list, extension_configs: dict = dict()) -> None:
    st.write(
        markdown.markdown(
            text,
            extensions=extensions,
            extension_configs=extension_configs,
        ),
        unsafe_allow_html=True,
    )


SUPPORTED_PLATFORMS = ("github", "notion", "twitter", "streamlit")
GITHUB_ICON = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
NOTION_ICON = "https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png"
TWITTER_ICON = "https://seeklogo.com/images/T/twitter-icon-circle-blue-logo-0902F48837-seeklogo.com.png"
STREAMLIT_ICON = "https://aws1.discourse-cdn.com/business7/uploads/streamlit/original/2X/f/f0d0d26db1f2d99da8472951c60e5a1b782eb6fe.png"


# TODO: Get the css thingy out of stx' mention!
# TODO: Create a Notion project so that "style" stop taking vertical space in Streamlit apps
def stx_mention(label: str, url: str, icon: str = "🔗", write: bool = True):
    """Mention a link with a label and icon.
    Args:
        label (str): Label to use in the mention
        icon (str): Icon to use. Can be an emoji or a URL. Default '🔗'
        url (str): Target URL of the mention
        write (bool): Writes the mention directly. If False, returns the raw HTML.
                      Useful if mention is used inline.
    """

    if icon.lower() == "github":
        icon = GITHUB_ICON
    elif icon.lower() == "notion":
        icon = NOTION_ICON
    elif icon.lower() == "twitter":
        icon = TWITTER_ICON
    elif icon.lower() == "streamlit":
        icon = STREAMLIT_ICON

    if validate_url(icon):
        icon_html = img(
            src=icon,
            style="width:1em;height:1em;vertical-align:-0.15em;border-radius:3px;margin-right:0.3em",
        )
    else:
        icon_html = icon + "  "

    mention_html = a(
        contenteditable=False,
        href=url,
        rel="noopener noreferrer",
        style="color:inherit;text-decoration:inherit; height:auto!important;margin-left:5px;",
        target="_blank",
    )(
        span(),
        icon_html,
        span(
            style=(
                "border-bottom:0.05em solid"
                " rgba(55,53,47,0.25);font-weight:500;flex-shrink:0;"
            )
        )(label),
        span(),
    )

    if write:
        st.write(str(mention_html), unsafe_allow_html=True)
    else:
        return str(mention_html)


class NicerArrowProcessor(InlineProcessor):
    def handleMatch(self, m: re.Match, data) -> Tuple[etree.Element, int, int]:
        """This function is called whenever a match is found.
        It will replace all arrows -> by the → character.
        """
        el = etree.Element("span")
        el.text = "→"
        return el, m.start(0), m.end(0)


class DoubleDashProcessor(InlineProcessor):
    def handleMatch(self, m: re.Match, data) -> Tuple[etree.Element, int, int]:
        """This function is called whenever a match is found.
        It will replace all double dashes -- by the — character.
        """
        el = etree.Element("span")
        el.text = "—"
        return el, m.start(0), m.end(0)


class AtSignProcessor(InlineProcessor):
    """Transforms '@(icon)(label)(url)' into HTML.
    Also works with '@(label)(url)' or '@(url)' in some cases.
    """

    @staticmethod
    def _add_https(url: str) -> str:
        if not url.startswith("https://"):
            url = "https://" + url
        return url

    def handleMatch(self, m: re.Match, data=None) -> Tuple[etree.Element, int, int]:
        """This function is called whenever a match is found.
        We want it to replace the '@(...)' pattern with an HTML element for the link.

        Args:
            m (re.Match): Match object
            data (_type_): [Not used - not sure what this does]

        Returns:
            (etree.Element, int, int): HTML element, with its starting and ending index.
        """
        groups = [group.strip("()") for group in m.groups() if group is not None]

        num_groups = len(groups)
        if num_groups == 1:
            url = groups[0]
            icon, label = self._guess_icon_and_label(url)
        elif num_groups == 2:
            label, url = groups
            icon, _ = self._guess_icon_and_label(url)
        elif num_groups == 3:
            icon, label, url = groups

        url = self._add_https(url)

        html = stx_mention(label=label, icon=icon, url=url, write=False)
        el = ET.ElementTree(ET.fromstring(str(html))).getroot()
        el.set("style", "display: inline; color:inherit; text-decoration:inherit;")
        return el, m.start(0), m.end(0)

    @staticmethod
    @st.experimental_memo
    def _get_favicon(url: str) -> str:
        return favicon.get(url)[0].url

    @staticmethod
    @st.experimental_memo
    def _get_page_title(url: str) -> str:
        n = requests.get(url)
        al = n.text
        return al[al.find("<title>") + 7 : al.find("</title>")]

    def _guess_icon_and_label(self, url: str) -> Tuple[str, str]:
        """Find out plausible icon and label from URL alone

        Args:
            url (str): URL of the link

        Returns:
            str: Icon of the link
            str: Label of the link
        """
        if "twitter.com" in url:
            icon = "twitter"
            # Tweet
            if "status" in url:
                label = url.split("twitter.com/")[1].split("/")[0]
            # Username
            else:
                label = url.split("/")[-1]
        elif (
            "streamlitapp.com" in url or "streamlit.io" in url or "streamlit.app" in url
        ):
            icon = "streamlit"
            label = "Streamlit App"
        elif "github.com" in url:
            icon = "github"
            label = "/".join(url.split("/")[-2:])
        elif "notion.so" in url:
            icon = "notion"
            label = "Notion page"
        else:
            try:
                icon = self._get_favicon(url)
                label = self._get_page_title(url)
            except Exception as e:
                st.write(e)
                icon = "🔗"
                label = "Link"
        return icon, label


class ColorProcessor(InlineProcessor):
    """Transforms '[red]Test[/red]' into HTML."""

    def handleMatch(self, m: re.Match, data=None) -> Tuple[etree.Element, int, int]:
        """This function is called whenever a match is found.

        Args:
            m (re.Match): Match object
            data (_type_): [Not used - not sure what this does]

        Returns:
            (etree.Element, int, int): HTML element, with its starting and ending index.
        """

        groups = list(m.groups())
        color = groups[0]
        content = groups[1]
        color_hex = ST_COLOR_PALETTE[color]["70"]
        html = span(style=f"color:{color_hex};")(content)
        el = ET.ElementTree(ET.fromstring(str(html))).getroot()
        return el, m.start(0), m.end(0)


# class AlignProcessor(InlineProcessor):
#     """Transforms '[right]Test[/right]' into HTML."""

#     def handleMatch(self, m: re.Match, data=None) -> Tuple[etree.Element, int, int]:
#         """This function is called whenever a match is found.

#         Args:
#             m (re.Match): Match object
#             data (_type_): [Not used - not sure what this does]

#         Returns:
#             (etree.Element, int, int): HTML element, with its starting and ending index.
#         """

#         groups = list(m.groups())
#         align = groups[0]
#         content = groups[1]
#         html = span(style=f"text-align: {align};")(content)
#         el = ET.ElementTree(ET.fromstring(str(html))).getroot()
#         return el, m.start(0), m.end(0)


class MarkdownLitExtension(Extension):
    def extendMarkdown(self, md):
        """This is a method to register a bunch of processors into a single Markdown extension."""

        ARROW_RE = r"->"
        md.inlinePatterns.register(
            item=NicerArrowProcessor(ARROW_RE, md), name="nicerarrow", priority=1_000
        )

        DOUBLE_DASH_RE = r"--"
        md.inlinePatterns.register(
            item=DoubleDashProcessor(DOUBLE_DASH_RE, md),
            name="doubledash",
            priority=1_000,
        )

        AT_SIGN_RE = r"@(?P<a>\([^)]+\))(?P<b>\([^)]+\))?(?P<c>\([^)]+\))?"
        md.inlinePatterns.register(
            item=AtSignProcessor(AT_SIGN_RE, md),
            name="atsign",
            priority=1_000,
        )

        SUPPORTED_COLORS = "|".join(ST_COLOR_PALETTE.keys())
        COLOR_RE = rf"\[(?P<color_open>{SUPPORTED_COLORS})\](?P<content>[^\[]+)\[\/(?P<color_close>{SUPPORTED_COLORS})\]"
        md.inlinePatterns.register(
            item=ColorProcessor(COLOR_RE, md),
            name="color",
            priority=1_000,
        )

        # SUPPORTED_ALIGNS = "|".join(["left", "right", "center", "justify"])
        # ALIGN_RE = rf"\[(?P<align_open>{SUPPORTED_ALIGNS})\](?P<content>[^\[]+)\[\/(?P<align_close>{SUPPORTED_ALIGNS})\]"
        # md.inlinePatterns.register(
        #     item=AlignProcessor(ALIGN_RE, md),
        #     name="align",
        #     priority=1_000,
        # )


mdlit = partial(
    md,
    extensions=[
        MarkdownLitExtension(),
        "pymdownx.details",
        "pymdownx.tasklist",
        "fenced_code",
    ],
)

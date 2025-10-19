from pydantic import Field

from pipelex.client.protocol import StuffContentOrData
from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.core.concepts.concept_native import NativeConceptCode
from pipelex.core.stuffs.list_content import ListContent
from pipelex.core.stuffs.structured_content import StructuredContent
from pipelex.core.stuffs.stuff import Stuff
from pipelex.core.stuffs.text_content import TextContent


class MySubClass(StructuredContent):
    arg4: str = Field(description="Test argument 4")


class MyConcept(StructuredContent):
    arg1: str = Field(description="Test argument 1")
    arg2: int = Field(description="Test argument 2")
    arg3: MySubClass = Field(description="Test argument 3")


TEST_CASES: list[tuple[str, StuffContentOrData, str, str, Stuff]] = [
    # Case 1.1: Content is a string
    (
        "case-1.1-string",
        "Lorem Ipsum",
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
            content=TextContent(text="Lorem Ipsum"),
        ),
    ),
    # Case 1.2: Content is a list of strings
    (
        "case-1.2-list-of-strings",
        ["Lorem Ipsum 1", "Lorem Ipsum 2", "Lorem Ipsum 3"],
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
            content=ListContent(
                items=[
                    TextContent(text="Lorem Ipsum 1"),
                    TextContent(text="Lorem Ipsum 2"),
                    TextContent(text="Lorem Ipsum 3"),
                ]
            ),
        ),
    ),
    # Case 1.3: Content is a StuffContent object
    (
        "case-1.3-stuff-content-object",
        MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
        ),
    ),
    # Case 1.4: Content is a list of StuffContent objects
    (
        "case-1.4-list-of-stuff-content-objects",
        [
            MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
            MyConcept(arg1="arg1_2", arg2=2, arg3=MySubClass(arg4="arg4_2")),
        ],
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=ListContent(
                items=[
                    MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
                    MyConcept(arg1="arg1_2", arg2=2, arg3=MySubClass(arg4="arg4_2")),
                ]
            ),
        ),
    ),
    # Case 2.1: Content is a string
    (
        "case-2.1-dict-with-string-content",
        {"concept": "Text", "content": "my text"},
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
            content=TextContent(text="my text"),
        ),
    ),
    # Case 2.1b: Content is a string with native prefix
    (
        "case-2.1b-dict-with-string-content-native-prefix",
        {"concept": "native.Text", "content": "my text"},
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
            content=TextContent(text="my text"),
        ),
    ),
    # case 2.1c: Content is a string but the concept is not native.Text, but a concept that refines Text
    (
        "case-2.1c-dict-with-string-content-not-native-text",
        {"concept": "test_domain.MyConceptNotNativeText", "content": "my text"},
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make(
                domain="test_domain",
                concept_code="MyConceptNotNativeText",
                description="Test concept for unit tests",
                structure_class_name="MyConceptNotNativeText",
                refines="native.Text",
            ),
            content=TextContent(text="my text"),
        ),
    ),
    # Case 2.2: Content is a list of strings
    (
        "case-2.2-dict-with-list-of-strings",
        {"concept": "Text", "content": ["text1", "text2", "text3"]},
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
            content=ListContent(
                items=[
                    TextContent(text="text1"),
                    TextContent(text="text2"),
                    TextContent(text="text3"),
                ]
            ),
        ),
    ),
    # case 2.2b: Content is a list of strings but the concept is not native.Text, but a concept that refines Text
    (
        "case-2.2b-dict-with-list-of-strings-not-native-text",
        {"concept": "test_domain.MyConceptNotNativeText", "content": ["text1", "text2", "text3"]},
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make(
                domain="test_domain",
                concept_code="MyConceptNotNativeText",
                description="Test concept for unit tests",
                structure_class_name="MyConceptNotNativeText",
                refines="native.Text",
            ),
            content=ListContent(
                items=[
                    TextContent(text="text1"),
                    TextContent(text="text2"),
                    TextContent(text="text3"),
                ]
            ),
        ),
    ),
    # Case 2.3: Content is a StuffContent object
    (
        "case-2.3-dict-with-stuff-content-object",
        {
            "concept": "test_domain.MyConcept",
            "content": MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
        },
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
        ),
    ),
    # Case 2.4: Content is a list of StuffContent objects
    (
        "case-2.4-dict-with-list-of-stuff-content-objects",
        {
            "concept": "test_domain.MyConcept",
            "content": [
                MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
                MyConcept(arg1="arg1_2", arg2=2, arg3=MySubClass(arg4="arg4_2")),
            ],
        },
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=ListContent(
                items=[
                    MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
                    MyConcept(arg1="arg1_2", arg2=2, arg3=MySubClass(arg4="arg4_2")),
                ]
            ),
        ),
    ),
    # Case 2.5: Content is a dict
    (
        "case-2.5-dict-with-dict-content",
        {
            "concept": "test_domain.MyConcept",
            "content": {
                "arg1": "something",
                "arg2": 1,
                "arg3": {"arg4": "something else else"},
            },
        },
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_code="stuff_code",
            stuff_name="stuff_name",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=MyConcept(arg1="something", arg2=1, arg3=MySubClass(arg4="something else else")),
        ),
    ),
    # Case 2.6: Content is a list of dicts
    (
        "case-2.6-dict-with-list-of-dicts",
        {
            "concept": "test_domain.MyConcept",
            "content": [
                {
                    "arg1": "something",
                    "arg2": 1,
                    "arg3": {"arg4": "something else else"},
                },
                {
                    "arg1": "something else",
                    "arg2": 2,
                    "arg3": {"arg4": "something else else else"},
                },
            ],
        },
        "stuff_name",
        "stuff_code",
        Stuff(
            stuff_name="stuff_name",
            stuff_code="stuff_code",
            concept=ConceptFactory.make(
                concept_code="MyConcept",
                domain="test_domain",
                description="Test concept for unit tests",
                structure_class_name="MyConcept",
            ),
            content=ListContent(
                items=[
                    MyConcept(arg1="something", arg2=1, arg3=MySubClass(arg4="something else else")),
                    MyConcept(arg1="something else", arg2=2, arg3=MySubClass(arg4="something else else else")),
                ]
            ),
        ),
    ),
]

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API")
)

if 'shutter-share' not in pc.list_indexes().names():
    pc.create_index(
        name='shutter-share',
        dimension=768,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
    )
)
index = pc.Index("shutter-share")
model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

def generate_and_store_embeddings(post):
    topics = []
    for topic in post.post_topics.all():
        if topic.self_portraits > 0.5:
            topics.append('Self Portraits')
        if topic.art > 0.5:
            topics.append('Art')
        if topic.fashion_style > 0.5:
            topics.append('Fashion Style')
        if topic.products > 0.5:
            topics.append('Products')
        if topic.creative_projects > 0.5:
            topics.append('Creative Projects')
        if topic.events > 0.5:
            topics.append('Events')
        if topic.photography_techniques > 0.5:
            topics.append('Photography Techniques')
        if topic.themes_challenges > 0.5:
            topics.append('Themes Challenges')
        if topic.inspiration_ideas > 0.5:
            topics.append('Inspiration Ideas')
        if topic.comparisons > 0.5:
            topics.append('Comparisons')
    post_content = f"{post.title} {post.description} {' '.join(topics)}"
    embeddings = model.encode(post_content, convert_to_tensor=True).tolist()
    index.upsert([(str(post.id), embeddings)])
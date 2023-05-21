from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import openai
import json
from openai.error import RateLimitError
from PIL import Image
import pytesseract
import io
import base64
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import heapq
from django.contrib.staticfiles import finders

# Create your views here.

allergy_words = ['나무이끼추출물', '리날룰', '리모넨', '메칠2-옥티노에이트', '벤질벤조에이트',
                 '벤질살리실레이트', '벤질신나메이트', '벤질알코올', '부틸페닐메칠프로피오날', '시트랄',
                 '시트로넬롤', '신나밀알코올', '신남알', '아니스에탄올', '아밀신나밀알코올',
                 '아밀신남알', '알파-이소메칠이오논', '유제놀', '이소유제놀', '제라니올',
                 '참나무이끼추출물', '쿠마린', '파네솔', '하이드록시시트로넬알', '하이드록시이소헥실3-사이클로헥센카복스알데하이드',
                 '헥실신남알']

harmful_ingredients = ['디부틸히드록시톨루엔', '옥시 벤존', '합성향료', '이소프로필 알코올', '파라벤',
                       '설페이트', '폴리에틸렌글리콜', '트리에탄올아민', '이소프로필 메틸페놀', '사이클로 펜타실록산',
                       '트리클로산', '미네랄오일', '페녹시에탄올', '티몰', '소르빅애씨드',
                       '트리이소프로판올아민', '파라핀', '이미디아 졸리디닐우레아', '부틸 하이드록시 아니솔', '합성착색료']


def index(request):
    return render(request, 'myapp/index.html')


@csrf_exempt
def chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get('message')

        if "hi" in message.lower():
            response_message = "안녕하세요! "
        elif "안녕" in message.lower():
            response_message = "안녕하세요! "
        elif "화장품 성분" in message.lower():
            response_message = "화장품 성분을 분석하기 위해 이미지를 업로드해주세요. "
        elif "안녕" in message.lower():
            response_message = "안녕하세요! "

        else:
            response_message = "죄송하지만 이해를 하지 못하였습니다."

        return JsonResponse({'response': response_message})
    return JsonResponse({'response': 'Invalid request'}, status=400)


@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        image = Image.open(io.BytesIO(request.FILES['image'].read()))
        text = pytesseract.image_to_string(image, lang='kor')

        index = text.find('[전성분]')
        if index == -1:
            return JsonResponse({'error': '전성분 정보가 없습니다.'})

        end = text.find('\n\n', index)
        if end == -1:
            end = len(text)
        paragraph = text[index:end]
        paragraph = paragraph.replace('\n', '')

        ingredients = paragraph.split(',')
        n = 5

        plist = [ingredients[i:i+n] for i in range(0, len(ingredients), n)]

        allergies = []
        harmful = []

        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if ingredient in allergy_words:
                allergies.append(ingredient)
            if ingredient in harmful_ingredients:
                harmful.append(ingredient)

        result = {}

        excel_file = finders.find('product_data.xlsx')
        df = pd.read_excel(excel_file)
        products = {row['제품명']: row['전성분'] for _, row in df.iterrows()}

        input_ingredients = ', '.join(ingredients)
        vectorizer = TfidfVectorizer()
        product_matrix = vectorizer.fit_transform(
            [input_ingredients] + list(products.values()))
        similarities = cosine_similarity(
            product_matrix[0:1], product_matrix[1:])[0]
        sorted_indices = heapq.nlargest(
            5, range(len(similarities)), similarities.take)
        top_similarities = similarities[sorted_indices]

        recommended_products = []
        for i, (product, similarity) in enumerate(zip(sorted_indices, top_similarities), 1):
            product_name = list(products.keys())[product]
            similarity_percent = (similarity + 1) / 2 * 100
            recommended_products.append({
                'name': product_name,
                'similarity': similarity_percent,
            })

        result['ingredients'] = []
        for i in range(len(plist)):
            result['ingredients'].append(", ".join(plist[i]))
        if len(allergies) > 0:
            result['allergy'] = allergies
        else:
            result['allergy'] = "알레르기 유발 성분이 포함되어 있지 않습니다."
        if len(harmful) > 0:
            result['harmful'] = harmful
        else:
            result['harmful'] = "유해성분이 포함되어 있지 않습니다."

        result['recommended_products'] = recommended_products

        return JsonResponse({'result': result})

    else:
        return JsonResponse({"error": "이미지 업로드에 실패했습니다."})

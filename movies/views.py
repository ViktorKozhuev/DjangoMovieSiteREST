from django.db import models
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Actor
from .serializers import (MovieListSerializer,
                          MovieDetailSerializer,
                          ReviewCreateSerializer,
                          CreateRatingSerializer,
                          ActorListSerializer,
                          ActorDetailSerializer)
from .service import get_client_ip


class MovieListView(APIView):

    def get(self, request):
        # movies = Movie.objects.filter(draft=False).annotate(
        #     rating_user=models.Case(
        #         models.When(ratings__ip=get_client_ip(request), then=True),
        #         default=False,
        #         output_field=models.BooleanField()
        #     ),
        # )
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)


class MovieDetailView(APIView):

    def get(self, request, pk):
        movie = Movie.objects.get(id=pk, draft=False)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)


class ReviewCreateView(APIView):

    def post(self, request):
        review = ReviewCreateSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=201)


class AddRatingStarView(APIView):

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        serializer = CreateRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip=get_client_ip(request))
            return Response(status=201)
        else:
            return Response(status=400)


class ActorsListView(generics.ListAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorListSerializer


class ActorsDetailView(generics.RetrieveAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer
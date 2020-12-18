import graphene
from graphene_django import DjangoObjectType

from cockroach.models import UserModel
# from posts.models import Article

import posts.schema


class UserType(DjangoObjectType):
    class Meta:
        model = UserModel


class Query(posts.schema.Query, graphene.ObjectType):
    # pass
    users = graphene.List(UserType)

    def resolve_users(self, info):
        return UserModel.objects.all()


class CreateUser(graphene.Mutation):
    # _id = graphene.Int()
    email = graphene.String()
    password = graphene.String()

    class Arguments:
        email = graphene.String()
        password = graphene.String()

    def mutate(self, info, email, password):
        user = UserModel(
          email=email,
          password=password,
        )
        user.save()

        return CreateUser(
            name=user.email,
            last_name=user.password,
        )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

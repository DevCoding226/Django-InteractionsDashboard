from django.utils.text import camel_case_to_spaces
from rest_framework import serializers
from collections import defaultdict, OrderedDict
from rest_auth.serializers import PasswordResetSerializer
from .models import (
    Comment,
    EngagementPlan,
    EngagementPlanHCPItem,
    EngagementPlanProjectItem,
    HCP,
    Project,
    HCPObjective,
    HCPDeliverable,
    ProjectObjective,
    ProjectDeliverable,
    AffiliateGroup,
    TherapeuticArea,
    Resource,
    Project,
    Interaction,
    User,
    BrandCriticalSuccessFactor,
    MedicalPlanObjective,
)


class NestedWritableFieldsSerializerMixin:
    """Mechanism for nestable writable fields.

    Goals: DRY, explicit, debuggable, easily extendable!
    """
    class Meta:
        # expect nested_fields : {field_name: {serializer, *parent_field_name}}
        # (just use an OrderedDict here if order matters)
        nested_fields = {}

    def validate(self, data):
        for field_name in self.Meta.nested_fields.keys():
            ids = set()
            for it in data.get(field_name, []):
                if 'id' not in it:
                    continue
                if it['id'] in ids:
                    raise serializers.ValidationError('duplicate {} id: {}'.format(field_name,
                                                                                   it['id']))
                ids.add(it['id'])
        return data

    def create(self, validated_data):
        nested_data = self._extract_nested_data(validated_data)

        # default create
        obj = super().create(validated_data)

        # handle nested objects
        for field_name, nested_items_data in nested_data.items():
            if nested_items_data is None:
                continue
            for item_data in nested_items_data:
                parent_field_name = self.Meta.nested_fields[field_name].get(
                    'parent_field_name', self._guess_parent_ref_field_name())
                item_data[parent_field_name] = obj.id
                serializer_class = self.Meta.nested_fields[field_name]['serializer']
                serializer = serializer_class(data=item_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return obj

    def update(self, obj, validated_data):
        nested_data = self._extract_nested_data(validated_data)

        # default create
        super().update(obj, validated_data)

        # handle nested objects
        for field_name, nested_items_data in nested_data.items():
            if nested_items_data is None:
                continue

            # delete items not present
            getattr(obj, field_name).exclude(
                id__in=(item_data['id']
                        for item_data in nested_items_data
                        if 'id' in item_data)
            ).delete()

            for item_data in nested_items_data:
                serializer_class = self.Meta.nested_fields[field_name]['serializer']
                model_class = serializer_class.Meta.model
                # update for those with id
                if 'id' in item_data:
                    serializer = serializer_class(
                        model_class.objects.get(id=item_data['id']),
                        item_data,
                        partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                # crate those without id
                else:
                    parent_field_name = self.Meta.nested_fields[field_name].get(
                        'parent_field_name', self._guess_parent_ref_field_name())
                    item_data[parent_field_name] = obj.id
                    serializer = serializer_class(data=item_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        return obj

    def _extract_nested_data(self, validated_data):
        """Extract nested data first so it doesn't break the regular process
        """
        nested_data = OrderedDict()
        for field_name in self.Meta.nested_fields.keys():
            nested_data[field_name] = validated_data.pop(field_name, None)
        return nested_data

    def _guess_parent_ref_field_name(self):
        """Hacky way to "guess" parent class-referencing field name
        """
        parent_field_name = (
            camel_case_to_spaces(self.Meta.model.__name__).replace(' ', '_') +
            '_id')
        return parent_field_name


class UserSerializer(serializers.ModelSerializer):
    group_names = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'group_names',
            'permissions',
            'first_name',
            'last_name',
            'affiliate_groups',
            'tas',
        )

    def get_group_names(self, user):
        return [group.name for group in user.groups.all()]

    def get_permissions(self, user):
        return user.get_all_permissions()


class AffiliateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateGroup
        fields = ('id', 'name')


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False, read_only=True)
    user = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user_id',
            'user',
            'engagement_plan',
            'engagement_plan_hcp_item',
            'engagement_plan_project_item',
            'hcp_objective',
            'project_objective',
            'hcp_deliverable',
            'project_deliverable',
            'message',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class BrandCriticalSuccessFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandCriticalSuccessFactor
        fields = (
            'id',
            'name',
            'ta_id',
            'affiliate_groups',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class MedicalPlanObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalPlanObjective
        fields = (
            'id',
            'name',
            'ta_id',
            'affiliate_groups',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'affiliate_groups',
            'tas',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class TherapeuticAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapeuticArea
        fields = ('id', 'name')


class ResourceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Resource
        fields = (
            'id',
            'user_id',
            'title',
            'description',
            'zinc_number_country',
            'zinc_number_global',
            'url',
            'file',
            'affiliate_groups',
            'tas',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class HCPSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCP
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'contact_person_first_name',
            'contact_person_last_name',
            'contact_person_email',
            'contact_person_phone',
            'time_availability',
            'institution_name',
            'institution_address',
            'contact_preference',
            'affiliate_groups',
            'tas',
            'tas_names',
            'city',
            'country',
            'has_consented',
            'interactions_count',
            'last_interaction',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
            'tas_names',
            'interactions_count',
            'last_interaction',
        )


class HCPDeliverableSerializer(serializers.ModelSerializer):
    objective_id = serializers.IntegerField(required=False)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = HCPDeliverable
        fields = (
            'id',
            'objective_id',
            'quarter',
            'quarter_type',
            'description',
            'status',
            'comments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class HCPObjectiveSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    hcp_id = serializers.IntegerField()
    engagement_plan_item_id = serializers.IntegerField(required=False)
    deliverables = HCPDeliverableSerializer(many=True)
    bcsf_id = serializers.IntegerField(allow_null=True, required=False)
    medical_plan_objective_id = serializers.IntegerField(allow_null=True, required=False)
    project_id = serializers.IntegerField(allow_null=True, required=False)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = HCPObjective
        fields = (
            'id',
            'engagement_plan_item_id',
            'hcp_id',
            'description',
            'bcsf_id',
            'medical_plan_objective_id',
            'project_id',
            'deliverables',
            'comments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'deliverables': {
                'serializer': HCPDeliverableSerializer,
                'parent_field_name': 'objective_id',
            }
        }


class ProjectDeliverableSerializer(serializers.ModelSerializer):
    objective_id = serializers.IntegerField(required=False)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = ProjectDeliverable
        fields = (
            'id',
            'objective_id',
            'quarter',
            'quarter_type',
            'description',
            'status',
            'comments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class ProjectObjectiveSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    project_id = serializers.IntegerField()
    engagement_plan_item_id = serializers.IntegerField(required=False)
    deliverables = ProjectDeliverableSerializer(many=True)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = ProjectObjective
        fields = (
            'id',
            'engagement_plan_item_id',
            'project_id',
            'description',
            'bcsf_id',
            'medical_plan_objective_id',
            'deliverables',
            'comments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'deliverables': {
                'serializer': ProjectDeliverableSerializer,
                'parent_field_name': 'objective_id',
            }
        }


class EngagementPlanHCPItemSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    engagement_plan_id = serializers.IntegerField(required=False)
    hcp_id = serializers.IntegerField()
    hcp = HCPSerializer(required=False, read_only=True)
    objectives = HCPObjectiveSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = EngagementPlanHCPItem
        fields = (
            'id',
            'engagement_plan_id',
            'hcp',
            'hcp_id',
            'objectives',
            'comments',
            'reason',
            'reason_other',
            'removed_at',
            'reason_removed',
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'objectives': {
                'serializer': HCPObjectiveSerializer,
                'parent_field_name': 'engagement_plan_item_id',
            }
        }


class EngagementPlanProjectItemItemSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    project = ProjectSerializer(required=False, read_only=True)
    project_id = serializers.IntegerField()
    engagement_plan_id = serializers.IntegerField(required=False)
    objectives = ProjectObjectiveSerializer(many=True)
    comments = CommentSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = EngagementPlanProjectItem
        fields = (
            'id',
            'engagement_plan_id',
            'project',
            'project_id',
            'removed_at',
            'reason_removed',
            'created_at',
            'updated_at',
            'objectives',
            'comments',
        )
        extra_kwargs = {'id': {'read_only': False, 'required': False}}
        nested_fields = {
            'objectives': {
                'serializer': ProjectObjectiveSerializer,
                'parent_field_name': 'engagement_plan_item_id',
            }
        }


class EngagementPlanSerializer(NestedWritableFieldsSerializerMixin, serializers.ModelSerializer):
    hcp_items = EngagementPlanHCPItemSerializer(many=True)
    project_items = EngagementPlanProjectItemItemSerializer(many=True)

    class Meta:
        model = EngagementPlan
        fields = (
            'id',
            'user_id',
            'year',
            'approved',
            'approved_at',
            'hcp_items',
            'project_items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'approved',
            'approved_at',
            'created_at',
            'updated_at',
        )
        nested_fields = {
            'hcp_items': {'serializer': EngagementPlanHCPItemSerializer},
            'project_items': {'serializer': EngagementPlanProjectItemItemSerializer},
        }

    def create(self, validated_data):
        # set user to current user unless user is admin
        user = self.context['request'].user
        if not user.is_staff and not user.is_superuser:
            validated_data['user'] = user

        return super().create(validated_data)


class InteractionSerializer(serializers.ModelSerializer):
    hcp = HCPSerializer(required=False)
    hcp_id = serializers.IntegerField()
    hcp_objective = HCPObjectiveSerializer(required=False)
    hcp_objective_id = serializers.IntegerField(required=False, allow_null=True)
    project = ProjectSerializer(required=False)
    project_id = serializers.IntegerField(required=False, allow_null=True)
    user = UserSerializer(required=False)

    class Meta:
        model = Interaction
        fields = (
            'id',
            'user_id',
            'user',
            'hcp',
            'hcp_id',
            'hcp_objective',
            'hcp_objective_id',
            'project',
            'project_id',
            'resources',
            'time_of_interaction',
            'purpose',
            'is_joint_visit',
            'is_joint_visit_manager_approved',
            'joint_visit_with',
            'joint_visit_reason',
            'joint_visit_reason_other',
            'origin_of_interaction',
            'origin_of_interaction_other',
            'type_of_interaction',
            'is_proactive',
            'is_adverse_event',
            'appropriate_pv_procedures_followed',
            'follow_up_date',
            'follow_up_notes',
            'no_follow_up_required',
            'created_at'
        )
        read_only_fields = (
            'created_at',
        )

    def create(self, validated_data):
        # set user to current user unless user is admin
        user = self.context['request'].user
        if not user.is_staff and not user.is_superuser:
            validated_data['user'] = user

        return super().create(validated_data)

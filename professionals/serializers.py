import re

from rest_framework import serializers

from .models import Professional


class ProfessionalSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField(read_only=True)
    contact = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Professional
        fields = [
            "id",
            "name",
            "profession",
            "address",
            "contact",
            "phone",
            "email",
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "zipcode",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "street": {"write_only": True},
            "number": {"write_only": True},
            "complement": {"write_only": True},
            "neighborhood": {"write_only": True},
            "city": {"write_only": True},
            "state": {"write_only": True},
            "zipcode": {"write_only": True},
            "phone": {"write_only": True},
            "email": {"write_only": True},
        }

    def get_address(self, obj):
        return obj.formatted_address()

    def get_contact(self, obj):
        return {"phone": obj.phone, "email": obj.email}

    def validate_name(self, value):
        """Strip leading and trailing whitespace from the name."""
        return value.strip()

    def validate_email(self, value):
        """Normalize email to lowercase and remove leading/trailing whitespace."""
        return value.lower().strip()

    def validate_phone(self, value):
        """
        Validate and clean phone number.

        Ensures the number has 10 or 11 digits (DDD + local number)
        and removes non-digit characters.
        Raises ValidationError if the length is incorrect.
        """
        clean_value = re.sub(r"[^\d]", "", value)

        if len(clean_value) < 10:  # DDD code + 8 digits
            raise serializers.ValidationError("O número de telefone é muito curto")
        if len(clean_value) > 11:  # DDD code + 9 digits
            raise serializers.ValidationError("O número de telefone é muito longo")

        return clean_value

    def validate_zipcode(self, value):
        """
        Validate and clean zipcode (CEP).

        Ensures the zipcode has exactly 8 digits. Removes non-digit characters.
        Raises ValidationError if the length is incorrect.
        """
        clean_value = re.sub(r"[^\d]", "", value)

        if len(clean_value) != 8:
            raise serializers.ValidationError("Formato de CEP inválido.")
        return clean_value


class PartialProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ["id", "name", "profession"]

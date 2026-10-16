import pulumi
import pulumi_openstack as openstack
from pulumi import ResourceOptions

resource_base_name = f"{pulumi.get_stack()}-osmit-overpass"
provider = openstack.Provider(
    resource_base_name,
    cloud="openstack",
    user_domain_name="Default",
    project_domain_id="default",
)
volume = openstack.blockstorage.Volume(
    resource_base_name,
    size=50,
    opts=ResourceOptions(provider=provider),
)
image = openstack.images.Image.get(
    resource_base_name,
    id="09ac7914-8b26-41c2-b5ab-9c2319ca9e9b",
    name="debian-13.0-trixie",
    opts=ResourceOptions(provider=provider),
)
instance = openstack.compute.Instance(
    resource_base_name,
    flavor_name="g4.cores4.ram8.disk20",
    security_groups=["default"],
    image_id=image.id,
    block_devices=[
        openstack.compute.InstanceBlockDeviceArgs(
            uuid=image.id,
            source_type="image",
            destination_type="local",
            boot_index=0,
            delete_on_termination=True,
        ),
        openstack.compute.InstanceBlockDeviceArgs(
            uuid=volume.id,
            source_type="volume",
            destination_type="volume",
            boot_index=1,
            delete_on_termination=True,
        ),
    ],
    networks=[
        {
            "name": "VXLAN/IPv6-dualstack",
        }
    ],
    opts=ResourceOptions(provider=provider),
)
pulumi.export("instance-name", instance.name)
pulumi.export(
    "instance-host",
    instance.name.apply(lambda name: f"{name}.osmit.eqiad1.wikimedia.cloud"),
)

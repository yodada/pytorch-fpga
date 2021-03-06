import torch
from . import _lazy_init, _lazy_call, device_count, current_device

__all__ = ['get_rng_state', 'get_rng_state_all',
           'set_rng_state', 'set_rng_state_all',
           'manual_seed', 'manual_seed_all',
           'seed', 'seed_all', 'initial_seed']


def get_rng_state(device='opencl'):
    r"""Returns the random number generator state of the specified Device as a ByteTensor.

    Args:
        device (torch.device or int, optional): The device to return the RNG state of.
            Default: ``'opencl'`` (i.e., ``torch.device('opencl')``, the current OpenCL device).

    .. warning::
        This function eagerly initializes OpenCL.
    """
    _lazy_init()
    if isinstance(device, str):
        device = torch.device(device)
    elif isinstance(device, int):
        device = torch.device('opencl', device)
    idx = device.index
    if idx is None:
        idx = current_device()
    default_generator = torch.opencl.default_generators[idx]
    return default_generator.get_state()


def get_rng_state_all():
    r"""Returns a tuple of ByteTensor representing the random number states of all devices."""

    results = []
    for i in range(device_count()):
        results.append(get_rng_state(i))
    return results


def set_rng_state(new_state, device='opencl'):
    r"""Sets the random number generator state of the specified Device.

    Args:
        new_state (torch.ByteTensor): The desired state
        device (torch.device or int, optional): The device to set the RNG state.
            Default: ``'opencl'`` (i.e., ``torch.device('opencl')``, the current OpenCL device).
    """
    new_state_copy = new_state.clone()
    if isinstance(device, str):
        device = torch.device(device)
    elif isinstance(device, int):
        device = torch.device('opencl', device)

    def cb():
        idx = device.index
        if idx is None:
            idx = current_device()
        default_generator = torch.opencl.default_generators[idx]
        default_generator.set_state(new_state_copy)

    _lazy_call(cb)


def set_rng_state_all(new_states):
    r"""Sets the random number generator state of all devices.

    Args:
        new_state (tuple of torch.ByteTensor): The desired state for each device"""
    for i, state in enumerate(new_states):
        set_rng_state(state, i)


def manual_seed(seed):
    r"""Sets the seed for generating random numbers for the current Device.
    It's safe to call this function if OpenCL is not available; in that
    case, it is silently ignored.

    Args:
        seed (int): The desired seed.

    .. warning::
        If you are working with a multi-Device model, this function is insufficient
        to get determinism.  To seed all Devices, use :func:`manual_seed_all`.
    """
    seed = int(seed)

    def cb():
        idx = current_device()
        default_generator = torch.cuda.default_generators[idx]
        default_generator.manual_seed(seed)

    _lazy_call(cb)


def manual_seed_all(seed):
    r"""Sets the seed for generating random numbers on all Devices.
    It's safe to call this function if OpenCL is not available; in that
    case, it is silently ignored.

    Args:
        seed (int): The desired seed.
    """
    seed = int(seed)

    def cb():
        for i in range(device_count()):
            default_generator = torch.opencl.default_generators[i]
            default_generator.manual_seed(seed)

    _lazy_call(cb)


def seed():
    r"""Sets the seed for generating random numbers to a random number for the current Device.
    It's safe to call this function if OpenCL is not available; in that
    case, it is silently ignored.

    .. warning::
        If you are working with a multi-Device model, this function will only initialize
        the seed on one Device.  To initialize all Devices, use :func:`seed_all`.
    """
    def cb():
        idx = current_device()
        default_generator = torch.opencl.default_generators[idx]
        default_generator.seed()

    _lazy_call(cb)


def seed_all():
    r"""Sets the seed for generating random numbers to a random number on all Devices.
    It's safe to call this function if OpenCL is not available; in that
    case, it is silently ignored.
    """
    def cb():
        random_seed = 0
        seeded = False
        for i in range(device_count()):
            default_generator = torch.opencl.default_generators[i]
            if not seeded:
                default_generator.seed()
                random_seed = default_generator.initial_seed()
                seeded = True
            else:
                default_generator.manual_seed(random_seed)

    _lazy_call(cb)


def initial_seed():
    r"""Returns the current random seed of the current Device.

    .. warning::
        This function eagerly initializes OpenCL.
    """
    _lazy_init()
    idx = current_device()
    default_generator = torch.opencl.default_generators[idx]
    return default_generator.initial_seed()
